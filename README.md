# LeggiMi

Trasforma documenti PDF in audiolibri intelligenti con intelligenza artificiale.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.21+-green.svg)](https://flet.dev/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-API-orange.svg)](https://openrouter.ai/)

## Descrizione

LeggiMi è uno strumento che trasforma PDF in audiolibri. Legge il documento, lo suddivide in capitoli, genera una spiegazione chiara e naturale in italiano e la trasforma in audio con sottotitoli.

### Caratteristiche

- ✅ **Estrae testo** da PDF, anche da scansioni (OCR con IA)
- ✅ **Suddivide automaticamente** in capitoli
- ✅ **Genera script audio** in due modalità: riassunto o dialogo
- ✅ **Tre livelli** di complessità: Base, Intermedio, Avanzato
- ✅ **Sintesi vocale** con voci naturali (Edge TTS)
- ✅ **Sottotitoli SRT** sincronizzati
- ✅ **Interfaccia grafica** intuitiva
- ✅ **Navigazione** nei sottotitoli durante la riproduzione

## Avvio rapido

### Installazione

```bash
git clone https://github.com/leggimi/leggimi.git
cd leggimi
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
Configurazione
```

Modifica il file .env con le tue credenziali:

```env
OPENROUTER_API_KEY=la_tua_chiave
IMAGE_MODEL=openai/gpt-4o-mini
TEXT_MODEL=openrouter/quasar-alpha
```

### Esecuzione

```bash
python -m leggimi.ui.app
```

### Compilazione

Crea un eseguibile standalone con PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "leggimi:leggimi" --add-data ".env:." --hidden-import "flet" --hidden-import "miniaudio" --hidden-import "edge_tts" leggimi/ui/app.py
```

L'eseguibile sarà in `dist/`.

## Documentazione

- [Guida all'installazione](setup.md) - Configurazione dell'ambiente
- [Come eseguire](run.md) - Avvio dell'applicazione
- [Architettura interna](internals.md) - Come funziona il programma
- [Compilazione con PyInstaller](build.md) - Creazione di un eseguibile
- [Ottenere una API Key](api.md) - Creazione account OpenRouter
- [Struttura dei file del progetto](structure.md) - Organizzazione del codice
- [Risoluzione problemi](trobleshoot.md) - Soluzioni ai problemi più comuni

## Requisiti

- [Python 3.10+](https://www.python.org/downloads/)

- [Chiave API OpenRouter](docs/api.md)

- Connessione Internet

## Contributi

Contributi, segnalazioni di bug e richieste di funzionalità sono benvenute!

## Licenza

MIT License
