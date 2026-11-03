"""Monta il video a partire da un piano JSON.

Uso: python monta.py piano.json

Formato del piano (percorsi relativi alla cartella del piano):
{
  "sorgente": "C:/.../video.mp4",
  "uscita": "video - test01.mp4",
  "durata": 68.8,                       facoltativa, di default quella della sorgente
  "larghezza": 1080, "altezza": 1920, "fps": 30,
  "loudness": -14, "true_peak": -1.5,
  "inserti": [
    {"file": "grafiche/scheda.png", "da": 13.58, "a": 18.10, "tipo": "dissolvenza"},
    {"file": "grafiche/pagina.png", "da": 4.38, "a": 7.38, "tipo": "zoom", "zoom": 0.07},
    {"file": "grafiche/logo.png", "da": 0, "a": 68.8, "tipo": "fisso"}
  ]
}
tipo: "fisso" (compare di colpo), "dissolvenza" (entra in 0,12 s), "zoom" (immagine a tutta pagina
con zoom lento; renderizzarla piu' grande del fotogramma per non perdere definizione).
Gli inserti si sovrappongono nell'ordine dell'elenco: l'ultimo sta sopra.
"""
import json, os, sys
import strumenti


def monta(percorso_piano):
    base = os.path.dirname(os.path.abspath(percorso_piano))
    with open(percorso_piano, encoding="utf-8") as f:
        p = json.load(f)
    ass = lambda x: x if os.path.isabs(x) else os.path.join(base, x)
    ff = strumenti.ffmpeg()
    W, H, FPS = p.get("larghezza", 1080), p.get("altezza", 1920), p.get("fps", 30)
    sorgente = ass(p["sorgente"])
    durata = p.get("durata") or strumenti.info(sorgente)["durata"]

    args = [ff, "-hide_banner", "-y", "-i", sorgente]
    fc = [f"[0:v]fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1[v0]"]
    ultimo = "v0"
    for k, ins in enumerate(p["inserti"], start=1):
        a, b, tipo, file = float(ins["da"]), float(ins["a"]), ins.get("tipo", "fisso"), ass(ins["file"])
        if tipo == "zoom":
            clip = os.path.splitext(file)[0] + "_zoom.mp4"
            n = max(1, round((b - a) * FPS))
            z = ins.get("zoom", 0.07)
            strumenti.esegui([ff, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS),
                              "-i", file, "-vf",
                              f"zoompan=z='1+{z}*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
                              "-frames:v", str(n), "-c:v", "libx264", "-crf", "16", clip], controlla=True)
            args += ["-itsoffset", f"{a:.3f}", "-i", clip]
            fc.append(f"[{k}:v]setsar=1[o{k}]")
        else:
            args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b - a:.3f}", "-itsoffset", f"{a:.3f}", "-i", file]
            dz = f",fade=in:st={a:.3f}:d=0.12:alpha=1" if tipo == "dissolvenza" else ""
            fc.append(f"[{k}:v]format=rgba{dz}[o{k}]")
        fc.append(f"[{ultimo}][o{k}]overlay=0:0:eof_action=pass:enable='between(t,{a:.3f},{b:.3f})'[v{k}]")
        ultimo = f"v{k}"
    fc.append(f"[0:a]loudnorm=I={p.get('loudness', -14)}:TP={p.get('true_peak', -1.5)}:LRA=11[a]")
    uscita = ass(p["uscita"])
    args += ["-filter_complex", ";".join(fc), "-map", f"[{ultimo}]", "-map", "[a]", "-t", f"{durata:.2f}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", uscita]
    strumenti.esegui(args, controlla=True)
    return uscita


if __name__ == "__main__":
    print("FATTO", monta(sys.argv[1]))
