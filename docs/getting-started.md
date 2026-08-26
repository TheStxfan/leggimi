# Getting Started

## Installazione

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
OPENROUTER_API_KEY=sk-or-v1-...
IMAGE_MODEL=google/...
TEXT_MODEL=nvidia/...
```

## Esecuzione

```bash
python main.py
```

## Compilazione

Crea un eseguibile standalone con PyInstaller usando lo spec file:

```bash
pip install pyinstaller
pyinstaller leggimi.spec --clean
```

L'eseguibile sarà in `dist/`. Per eseguirlo, assicurati che il file `.env` sia nella stessa cartella di LeggiMi.
