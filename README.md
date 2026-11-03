# Video editing per Marketing Ignorante

Un sistema per montare video parlati brevi (reel, short) con **Claude Code**: trascrive con i tempi di ogni parola,
verifica i numeri detti, propone un piano di montaggio, disegna schede e sottotitoli in uno stile scritto,
esporta il video e lo controlla. Ogni correzione diventa una regola per il video successivo.

Nato per [Marketing Ignorante](https://www.instagram.com/marketing.ignorante/), che sta lanciando una rubrica video.

> **Stato: versione 0.1, in costruzione.** Testato su un video (un reel già montato, a cui sono state aggiunte
> grafiche sopra). Il montaggio da girato grezzo, la musica e gli effetti sonori non sono ancora stati provati.

## Cosa fa

1. **Ispeziona il file** e capisce se è girato grezzo o già montato.
2. **Trascrive** in locale (faster-whisper) con i tempi di ogni parola: velocità del parlato, pause, punti di taglio.
3. **Verifica i fatti**: ogni numero detto viene cercato sul web. Quelli senza fonte non vanno a schermo.
4. **Propone un piano di montaggio** (tempo, cosa, perché, fonte) e **aspetta l'approvazione**.
5. **Monta**: schede numero con fonte, ricostruzioni, immagini a tutta pagina, sottotitoli rifatti sulla parola pronunciata, cartello finale, logo.
6. **Controlla**: volume (-14 LUFS), picco, pause, e una griglia di fotogrammi da guardare prima di consegnare.
7. **Impara**: le correzioni finiscono in un registro. Alla terza ripetizione diventano regole nel documento di stile.

Il principio che regge tutto: ogni elemento a schermo deve far **capire**, **provare** o **segnalare**.
Il resto è decorazione.

## Cosa c'è

```
video-editing/                  la skill: copiala in .claude/skills/ del tuo progetto (o in ~/.claude/skills/)
├── SKILL.md                    istruzioni per Claude: flusso in 8 fasi e regole tecniche
├── installa.ps1                installazione degli strumenti (Windows)
├── requirements.txt
├── scripts/
│   ├── trascrivi.py            parole con tempi, velocità, pause
│   ├── analizza_reference.py   misure di un video di riferimento + fogli di fotogrammi
│   ├── grafiche.py             sottotitoli, schede numero, cartello finale, logo
│   ├── monta.py                esporta il video da un piano JSON
│   └── controlla.py            volume, picco, pause, griglia di fotogrammi
├── references/
│   ├── guida-montaggio.md      22 regole ricavate dall'analisi di tre reel
│   └── stile-video-esempio.md  lo stile video di Marketing Ignorante, da copiare e adattare
└── assets/font/                Poppins (licenza SIL OFL)
```

## Installazione

1. Copia la cartella `video-editing` in `.claude/skills/` del tuo progetto.
2. Installa gli strumenti, una volta sola:
   - **Windows:** `powershell -ExecutionPolicy Bypass -File .claude\skills\video-editing\installa.ps1`
     (crea un ambiente Python in `%LOCALAPPDATA%\mi-video-editing` con ffmpeg, trascrittore e librerie grafiche).
   - **Mac e Linux:** `python3 -m venv ~/.mi-video-editing && ~/.mi-video-editing/bin/pip install -r .claude/skills/video-editing/requirements.txt`.
     Non ancora testato.
3. Copia `references/stile-video-esempio.md` in `knowledge/video/stile-video.md` e adattalo al tuo brand.
4. Apri Claude Code e scrivi: "monta il video che è in Download". La skill si attiva da sola.

Serve Python 3.10 o superiore. Il primo avvio della trascrizione scarica il modello di riconoscimento vocale (alcune centinaia di MB).

## Dove funziona

| Ambiente | Cosa puoi fare |
|---|---|
| Claude Code sul tuo computer | Tutto |
| Cowork | Da provare: dipende dall'accesso alle cartelle e dalla possibilità di installare ffmpeg |
| claude.ai | Solo pianificazione: analisi del copione, verifica dei numeri, piano di montaggio. I file video 4K sono troppo pesanti da caricare |

## Licenza

Codice e documenti: MIT (vedi `LICENSE`). Font Poppins: SIL Open Font License (vedi `video-editing/assets/font/OFL.txt`).
I loghi e i video dei brand che monti restano dei rispettivi proprietari: verifica sempre la licenza di ciò che metti a schermo.
