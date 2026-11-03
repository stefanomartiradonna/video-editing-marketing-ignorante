"""Trascrizione locale con i tempi di ogni parola.

Uso: python trascrivi.py <video> [--lingua it] [--modello small] [--uscita cartella]
Produce: parole.json ([inizio, fine, parola]), trascrizione.txt, e stampa velocita' e pause.
"""
import argparse, json, os, wave
import strumenti


def trascrivi(video, lingua="it", modello="small", cartella=None):
    strumenti.prepara_dll()
    import numpy as np
    from faster_whisper import WhisperModel

    cartella = cartella or os.path.join(os.path.dirname(os.path.abspath(video)), "analisi")
    os.makedirs(cartella, exist_ok=True)
    wav = strumenti.estrai_wav(video, os.path.join(cartella, "audio.wav"))
    with wave.open(wav, "rb") as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    segs, _ = WhisperModel(modello, device="cpu", compute_type="int8").transcribe(
        audio, language=lingua, word_timestamps=True, vad_filter=False)
    parole, righe = [], []
    for s in segs:
        righe.append(f"[{s.start:6.2f} - {s.end:6.2f}] {s.text.strip()}")
        parole += [[round(float(w.start), 2), round(float(w.end), 2), w.word.strip()] for w in s.words]
    with open(os.path.join(cartella, "parole.json"), "w", encoding="utf-8") as f:
        json.dump(parole, f, ensure_ascii=False)
    with open(os.path.join(cartella, "trascrizione.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(righe))
    return parole, rapporto(parole)


def rapporto(parole):
    if not parole:
        return {}
    pause = [(parole[i][1], round(parole[i + 1][0] - parole[i][1], 2), parole[i][2]) for i in range(len(parole) - 1)]
    durata = parole[-1][1] - parole[0][0]
    return {
        "parole": len(parole),
        "parole_al_minuto": round(len(parole) / durata * 60) if durata else None,
        "prima_parola_s": parole[0][0],
        "ultima_parola_fine_s": parole[-1][1],
        "pausa_massima_s": max((p[1] for p in pause), default=0),
        "pause_oltre_0_3s": [{"dopo_s": p[0], "durata_s": p[1], "dopo_la_parola": p[2]} for p in pause if p[1] >= 0.3],
    }


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("video")
    a.add_argument("--lingua", default="it")
    a.add_argument("--modello", default="small")
    a.add_argument("--uscita")
    x = a.parse_args()
    _, r = trascrivi(x.video, x.lingua, x.modello, x.uscita)
    print(json.dumps(r, ensure_ascii=False, indent=1))
