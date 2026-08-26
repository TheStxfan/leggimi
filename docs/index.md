# LeggiMi

Trasforma documenti PDF in audiolibri intelligenti con intelligenza artificiale.

LeggiMi è uno strumento che legge un PDF, lo suddivide in capitoli, genera una spiegazione chiara e naturale in italiano (in modalità riassunto o dialogo) e la trasforma in audio MP3 con sottotitoli SRT sincronizzati.

## Caratteristiche principali

- **Estrazione automatica del testo** dai PDF (anche da scansioni)
- **Suddivisione in capitoli** basata sulla struttura del documento
- **Generazione di script audio** in due modalità:
  - _Riassunto_: spiegazione discorsiva con un singolo speaker
  - _Dialogo_: conversazione tra due speaker per una fruizione più coinvolgente
- **Tre livelli di complessità**: Base, Intermedio, Avanzato
- **Sintesi vocale** con voci naturali Edge TTS
- **Sottotitoli SRT** sincronizzati con l'audio
- **Interfaccia grafica** intuitiva con Flet
- **Riproduzione con navigazione** tra le righe dei sottotitoli

## Requisiti

- Python 3.10 o superiore
- Chiave API OpenRouter (per l'estrazione del testo e la generazione degli script)
- Connessione Internet (per le API)

> **Piattaforme supportate**: L'applicazione è attualmente testata e sviluppata **solo su Linux**. Il supporto per Windows e macOS non è garantito e potrebbe richiedere modifiche al codice o alla procedura di compilazione.

## Documentazione

- [Guida all'installazione](setup.md) - Configurazione dell'ambiente
- [Come eseguire](run.md) - Avvio dell'applicazione
- [Architettura interna](internals.md) - Come funziona il programma
- [Compilazione con PyInstaller](build.md) - Creazione di un eseguibile
- [Ottenere una API Key](api.md) - Creazione account OpenRouter
- [Struttura dei file del progetto](structure.md) - Organizzazione del codice
- [Risoluzione problemi](trobleshoot.md) - Soluzioni ai problemi più comuni

## Screenshots

[Interfaccia utente](images.md)
