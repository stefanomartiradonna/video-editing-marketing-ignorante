---
name: video-editing
description: Monta video parlati brevi per i social (reel, short, 30-90 secondi) con Claude Code. Trascrive con i tempi di ogni parola, verifica i numeri detti, propone un piano di montaggio da approvare, disegna schede, sottotitoli e cartelli nello stile della testata, esporta il video e lo controlla. Analizza anche video di riferimento per ricavarne regole di montaggio. Usa quando l'utente dice "monta questo video", "edita il video", "fai l'editing di", "editing video", "aggiungi le grafiche al video", "piano di montaggio", "analizza questi reel", "com'è montato questo video", "video di riferimento". Non usare per scrivere copioni, post o caroselli.
---

# Video editing per Marketing Ignorante

Sistema per montare talking head brevi con schede, sottotitoli e cartelli coerenti con uno stile scritto.
Il principio: ogni elemento a schermo deve far **capire**, **provare** o **segnalare**. Il resto è decorazione.

## 1. Cosa leggere prima di iniziare

1. **Documento di stile**: `knowledge/video/stile-video.md` nel progetto in cui lavori.
   Se non esiste, parti da `references/stile-video-esempio.md` (lo stile di Marketing Ignorante):
   copialo in `knowledge/video/stile-video.md` e adattalo con l'utente prima di montare.
2. **Registro correzioni**: `knowledge/video/registro-correzioni.md`, se esiste. Le correzioni registrate valgono come regole.
3. **Guida al montaggio**: `references/guida-montaggio.md` (pattern ricavati da tre reel di riferimento).
4. **Voce della testata**: `knowledge/voce.md`, se esiste, per ogni testo a schermo.

## 2. Dove gira

- **Claude Code sul computer dell'utente**: tutte le fasi.
- **claude.ai o Cowork senza ffmpeg o senza accesso ai file video**: solo le fasi 1-4 (analisi del copione,
  verifica dei numeri, piano di montaggio). Dillo all'utente all'inizio, non scoprirlo a metà.

## 3. Strumenti

- Installazione una volta: `powershell -ExecutionPolicy Bypass -File <cartella della skill>/installa.ps1`.
  Su Mac o Linux: crea un venv e `pip install -r requirements.txt` (non ancora testato).
- Python da usare: `%LOCALAPPDATA%\mi-video-editing\.venv\Scripts\python.exe`.
- Script in `scripts/` (lanciali da quella cartella, o aggiungila al percorso):
  - `trascrivi.py <video>`: parole con tempi, velocità, pause.
  - `analizza_reference.py <video>`: misure di un video di riferimento + fogli di fotogrammi.
  - `grafiche.py`: mattoni grafici (sottotitolo, scheda numero, cartello finale, logo testata).
  - `monta.py piano.json`: esporta il video sovrapponendo gli inserti.
  - `controlla.py <video> --tempi ... --parole ...`: volume, picco, pause, griglia di fotogrammi.
- Font: Poppins (licenza OFL) in `assets/font/`.

## 4. Flusso di lavoro

**Fase 1. Ispeziona il file.** Formato, durata, fps. Capisci se è **girato grezzo** o **già montato**
(sottotitoli impressi nell'immagine). Se è già montato puoi solo aggiungere elementi sopra: dillo subito
e proponi di recuperare il grezzo.

**Fase 2. Analizza.** `trascrivi.py`, poi un foglio di fotogrammi ogni 2 secondi. Individua:
tratti con sola faccia oltre 6 s, numeri detti, momenti in cui si parla della campagna senza mostrarla,
testo sopra immagini piene.

**Fase 3. Verifica i fatti.** Ogni numero e ogni affermazione da mettere a schermo va cercato sul web
(fonte primaria se c'è: premio, comunicato, testata). Un numero non verificato **non va a schermo**:
segnalalo all'utente con quello che dicono le fonti.

**Fase 4. Piano di montaggio e approvazione.** Tabella: tempo, cosa, perché, fonte. Aggiungi cosa NON
si può fare su quel file. **Fermati e aspetta l'approvazione dell'utente.** Se l'utente fa una domanda,
rispondi: non montare.

**Fase 5. Monta.** Crea `video-editing/progetti/<NOME>/` con:
`costruisci.py` (disegna le grafiche con `grafiche.py` e scrive `piano.json`), `asset/`, `grafiche/`.
Poi `monta.py piano.json`. I file video non vanno mai in git.

**Fase 6. Controlla.** `controlla.py` sul file esportato, poi **guarda la griglia**: testo che copre
il volto o altro testo, scritte tagliate, nomi sbagliati, sottotitoli coperti. Correggi e riesporta
prima di consegnare. Ripeti il controllo dopo ogni correzione.

**Fase 7. Consegna.** Percorso del file, elenco delle modifiche con i tempi, cosa non è verificato,
limiti. Aggiorna `piano-montaggio.md` nella cartella del progetto.

**Fase 8. Impara.** Ogni correzione dell'utente va in `knowledge/video/registro-correzioni.md`
(data, video, correzione, regola che ne deriva). Quando la stessa correzione arriva 3 volte, diventa
una regola nel documento di stile.

## 5. Regole tecniche già imparate

- Le schede coprono la parte alta (0-1300 px su 1920) e lasciano visibili i sottotitoli del video sotto.
- Se una grafica copre i sottotitoli impressi, rifai i sottotitoli di quel tratto con `sottotitoli_da_parole`
  usando i tempi di `parole.json`: stessa posizione, parola pronunciata su riquadro blu.
- Sotto ogni numero, la fonte in piccolo. Le ricostruzioni (annunci, schermate) portano la scritta "Ricostruzione".
- Loghi di brand: da Wikimedia Commons, controllando la licenza nella pagina del file. Annota la provenienza
  di ogni elemento nel piano: se arriva una segnalazione sui diritti si sa cosa sostituire.
- Immagini a tutta pagina con zoom: renderizzale 1,5 volte più grandi del fotogramma.
- Esporta 1080x1920, 30 fps, -14 LUFS, picco sotto -1 dB.
- Su Windows il venv sta in un percorso corto: i percorsi lunghi fanno fallire l'installazione.
