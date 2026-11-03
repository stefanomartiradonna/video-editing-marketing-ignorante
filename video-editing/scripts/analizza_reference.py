"""Analisi di un video di riferimento: ritmo, tagli, audio, parole.

Uso: python analizza_reference.py <video> [--lingua it] [--uscita cartella]
Produce nella cartella: fogli di fotogrammi (1 al secondo), parole.json, trascrizione.txt, rapporto.md.
Il rapporto contiene solo misure: l'interpretazione (cosa aiuta a capire, cosa e' decorativo) la fa Claude
guardando i fogli di fotogrammi.
"""
import argparse, json, os
import strumenti
from trascrivi import trascrivi


def analizza(video, lingua="it", cartella=None):
    nome = os.path.splitext(os.path.basename(video))[0]
    cartella = cartella or os.path.join(os.path.dirname(os.path.abspath(video)), f"analisi-{nome}")
    os.makedirs(cartella, exist_ok=True)
    inf, vol = strumenti.info(video), strumenti.loudness(video)
    netti = strumenti.tagli(video, 0.25)
    eventi = strumenti.raggruppa(strumenti.tagli(video, 0.08))
    strumenti.esegui([strumenti.ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-vf",
                      "fps=1,scale=216:-2,tile=8x5", os.path.join(cartella, "fotogrammi_%02d.png")], controlla=True)
    parole, rap = trascrivi(video, lingua, cartella=cartella)
    righe_tagli = []
    for t in netti:
        dentro = [w for w in parole if w[0] + 0.03 < t < w[1] - 0.03]
        righe_tagli.append(f"| {t:.2f} | {dentro[0][2] if dentro else 'no'} |")
    durata = inf["durata"] or 1
    testo = [
        f"# Analisi: {nome}", "",
        f"- Durata: {inf['durata']} s, {inf['larghezza']}x{inf['altezza']}, {inf['fps']} fps",
        f"- Volume medio: {vol['lufs']} LUFS, picco {vol['picco']} dB",
        f"- Cambi netti (soglia 0,25): {len(netti)}, uno ogni {durata / max(len(netti), 1):.1f} s",
        f"- Eventi visivi (soglia 0,08, raggruppati): {len(eventi)}, uno ogni {durata / max(len(eventi), 1):.1f} s",
        f"- Parole al minuto: {rap.get('parole_al_minuto')}, prima parola a {rap.get('prima_parola_s')} s, "
        f"pausa massima {rap.get('pausa_massima_s')} s",
        "", "## Tagli rispetto alle parole", "", "| Taglio (s) | Cade dentro la parola |", "|---|---|", *righe_tagli,
        "", "## Limiti", "",
        "- Fotogrammi a 1 al secondo: effetti piu' brevi possono sfuggire.",
        "- Audio misurato, non ascoltato: musica ed effetti sonori non sono identificati.",
        "- Tempi delle parole con margine di circa 0,1-0,2 s.",
    ]
    with open(os.path.join(cartella, "rapporto.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(testo))
    return os.path.join(cartella, "rapporto.md")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("video")
    a.add_argument("--lingua", default="it")
    a.add_argument("--uscita")
    x = a.parse_args()
    print(analizza(x.video, x.lingua, x.uscita))
