"""Controlli finali su un video esportato.

Uso: python controlla.py <video> [--tempi 2,4.6,15] [--parole parole.json] [--uscita griglia.png]
Stampa: formato, durata, volume, picco, e (se c'e' parole.json) voce iniziale e pause.
Salva una griglia di fotogrammi da guardare: i controlli visivi (testo che copre il volto,
scritte sovrapposte, errori nei nomi) si fanno guardando quella griglia.
"""
import argparse, json, os
import strumenti

OBIETTIVI = {"lufs": (-15.0, -13.0), "picco_max": -1.0, "voce_entro_s": 0.1, "pausa_max_s": 0.6}


def controlla(video, tempi=None, parole=None, uscita=None):
    inf, vol = strumenti.info(video), strumenti.loudness(video)
    esito = {"video": video, **inf, **vol, "avvisi": []}
    if vol["lufs"] is not None and not (OBIETTIVI["lufs"][0] <= vol["lufs"] <= OBIETTIVI["lufs"][1]):
        esito["avvisi"].append(f"Volume {vol['lufs']} LUFS fuori da -15/-13")
    if vol["picco"] is not None and vol["picco"] > OBIETTIVI["picco_max"]:
        esito["avvisi"].append(f"Picco {vol['picco']} dB sopra {OBIETTIVI['picco_max']} dB")
    if parole:
        with open(parole, encoding="utf-8") as f:
            w = json.load(f)
        if w and w[0][0] > OBIETTIVI["voce_entro_s"]:
            esito["avvisi"].append(f"La voce parte a {w[0][0]} s")
        lunghe = [(w[i][1], round(w[i + 1][0] - w[i][1], 2)) for i in range(len(w) - 1)
                  if w[i + 1][0] - w[i][1] > OBIETTIVI["pausa_max_s"]]
        if lunghe:
            esito["avvisi"].append(f"Pause oltre {OBIETTIVI['pausa_max_s']} s: {lunghe}")
    d = inf["durata"] or 0
    tempi = tempi or [round(d * k / 13, 1) for k in range(14)]
    uscita = uscita or os.path.splitext(video)[0] + " - controllo.png"
    esito["griglia"] = strumenti.griglia(video, [t for t in tempi if t < d], uscita)
    return esito


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("video")
    a.add_argument("--tempi")
    a.add_argument("--parole")
    a.add_argument("--uscita")
    x = a.parse_args()
    t = [float(v) for v in x.tempi.split(",")] if x.tempi else None
    print(json.dumps(controlla(x.video, t, x.parole, x.uscita), ensure_ascii=False, indent=1))
