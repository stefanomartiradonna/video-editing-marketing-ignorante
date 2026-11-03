"""Funzioni comuni: ffmpeg, informazioni sul video, volume, estrazione audio."""
import os, re, subprocess, sys


def prepara_dll():
    """Su Windows le librerie del trascrittore cercano le DLL di Visual C++ nella cartella del venv."""
    if os.name == "nt":
        for d in {sys.prefix, os.path.dirname(sys.executable)}:
            if os.path.isdir(d):
                try:
                    os.add_dll_directory(d)
                except OSError:
                    pass


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def esegui(args, controlla=False):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if controlla and r.returncode != 0:
        raise RuntimeError(r.stderr[-3000:])
    return r


def info(video):
    """Durata (s), larghezza, altezza, fps del primo flusso video."""
    err = esegui([ffmpeg(), "-hide_banner", "-i", video]).stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    durata = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else None
    v = re.search(r"Video: .*?, (\d{2,5})x(\d{2,5}).*?, ([\d.]+) fps", err)
    return {
        "durata": round(durata, 2) if durata else None,
        "larghezza": int(v.group(1)) if v else None,
        "altezza": int(v.group(2)) if v else None,
        "fps": float(v.group(3)) if v else None,
    }


def loudness(video):
    """Volume medio integrato (LUFS) e picco reale (dBTP)."""
    err = esegui([ffmpeg(), "-hide_banner", "-i", video, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)
    return {"lufs": float(i[-1]) if i else None, "picco": float(p[-1]) if p else None}


def estrai_wav(video, wav):
    esegui([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", wav], controlla=True)
    return wav


def tagli(video, soglia=0.25):
    """Tempi (s) dei cambi di scena sopra la soglia."""
    err = esegui([ffmpeg(), "-hide_banner", "-i", video, "-an", "-vf", f"select='gt(scene,{soglia})',showinfo",
                  "-f", "null", "-"]).stderr
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", err)]


def raggruppa(tempi, distanza=0.4):
    """Una transizione animata produce piu' fotogrammi vicini: li conta come un evento solo."""
    eventi, ultimo = [], -99.0
    for t in tempi:
        if t - ultimo > distanza:
            eventi.append(t)
        ultimo = t
    return eventi


def griglia(video, tempi, uscita, larghezza=360, colonne=7):
    """Un'immagine con i fotogrammi ai tempi indicati, ciascuno con il tempo scritto sopra."""
    from PIL import Image, ImageDraw
    cartella = os.path.dirname(os.path.abspath(uscita))
    pezzi = []
    for k, t in enumerate(tempi):
        f = os.path.join(cartella, f"_g{k:02d}.png")
        esegui([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", video,
                "-frames:v", "1", "-vf", f"scale={larghezza}:-2", f], controlla=True)
        im = Image.open(f).convert("RGB")
        ImageDraw.Draw(im).rectangle((0, 0, 90, 30), fill=(0, 0, 0))
        ImageDraw.Draw(im).text((6, 6), f"{t:.1f}s", fill=(255, 230, 0))
        pezzi.append(im)
        os.remove(f)
    righe = (len(pezzi) + colonne - 1) // colonne
    w, h = pezzi[0].size
    tela = Image.new("RGB", (w * min(colonne, len(pezzi)), h * righe))
    for k, im in enumerate(pezzi):
        tela.paste(im, ((k % colonne) * w, (k // colonne) * h))
    tela.save(uscita)
    return uscita
