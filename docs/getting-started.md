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
OPENROUTER_API_KEY=la_tua_chiave
IMAGE_MODEL=openai/gpt-4o-mini
TEXT_MODEL=openrouter/quasar-alpha
```

## Esecuzione

```bash
python -m leggimi.ui.app
```

## Compilazione

Crea un eseguibile standalone con PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "leggimi:leggimi" --add-data ".env:." --hidden-import "flet" --hidden-import "miniaudio" --hidden-import "edge_tts" leggimi/ui/app.py
```

L'eseguibile sarà in `dist/`.
