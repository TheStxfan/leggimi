# Pipeline di elaborazione

## 1. Estrazione del testo (`extractor.py`)

- Utilizza PyMuPDF per leggere il PDF
- Per PDF scansionati: invia ogni pagina al modello `IMAGE_MODEL` per l'OCR
- Rimuove sillabazione e unisce le righe

## 2. Segmentazione (`segmenter.py`)

- Analizza il testo per individuare titoli di capitolo (linee che iniziano con `#`)
- Crea oggetti `Chapter` con titolo e testo

## 3. Generazione script (`scriptgen.py`)

- Divide il testo del capitolo in blocchi di ~1500 parole (con overlap)
- Per ogni blocco: invia al modello `TEXT_MODEL` con il prompt appropriato
- Valida il formato della risposta (SPEAKER/TEXT)
- Supporta due modalità:
  - `riassunto`: singolo speaker
  - `dialogo`: due speaker (Speaker1 spiega, Speaker2 chiede)

## 4. Sintesi vocale (`tts.py`)

- Utilizza Edge TTS per generare audio da ogni battuta
- Combina i segmenti con ffmpeg
- Crea file SRT con i timestamp sincronizzati

## 5. Riproduzione (`audio_player.py` e `playback_lines.py`)

- `AudioPlayer`: gestisce la riproduzione con `miniaudio`
- `PlaybackLines`: visualizza e gestisce la navigazione dei sottotitoli

# Gestione della cache

I capitoli estratti vengono salvati in `cache/chapters/` come JSON. La chiave è l'hash SHA256 del PDF, quindi la cache è automaticamente invalidata se il documento cambia.

# Gestione errori

Tutti gli errori ereditano da `LeggiMiError`, con specializzazioni per:

- `PdfIlleggibileError`: PDF non leggibile o vuoto
- `LLMNonDisponibileError`: API non configurata o non raggiungibile
- `AudioPlaybackError`: problemi durante la riproduzione
- `InvalidScriptFormatError`: risposta del modello malformata
- `ChapterCacheError`: problemi con la cache
