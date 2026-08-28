# Guida all'installazione

> **Nota**: Questa applicazione è sviluppata e testata **esclusivamente su Linux**. Le istruzioni per Windows e macOS sono fornite a titolo indicativo e potrebbero non funzionare correttamente senza adattamenti.

## 1. Clonare il repository

```bash
git clone https://github.com/TheStxfan/leggimi.git
cd leggimi
```

## 2. Creare l'ambiente virtuale

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

## 3. Installare le dipendenze

```bash
pip install -r requirements.txt
```

## 4. Configurare le variabili d'ambiente

Copia il file `.env.example` e rinominalo in `.env`:

```bash
cp .env.example .env
```

> Nota: In modalità sviluppo, il .env deve stare nella root del progetto (dove c'è main.py). Nella versione compilata, deve stare nella stessa cartella dell'eseguibile.

Apri il file `.env` e inserisci le tue credenziali:

```env
# Chiave API per OpenRouter (obbligatoria)
OPENROUTER_API_KEY=sk-or-v1-...

# Modello per l'estrazione del testo dalle immagini PDF
IMAGE_MODEL=google/...

# Modello per la generazione degli script
TEXT_MODEL=nvidia/...
```

[Ottieni la chiave API gratuita](api.md)

### Variabili disponibili

| Variabile            | Descrizione                             | Obbligatoria |
| :------------------- | :-------------------------------------- | :----------: |
| `OPENROUTER_API_KEY` | Chiave API di OpenRouter                |    ✅ Sì     |
| `IMAGE_MODEL`        | Modello per l'OCR su immagini PDF       |    ✅ Sì     |
| `TEXT_MODEL`         | Modello per la generazione degli script |    ✅ Sì     |

### Come trovare i migliori modelli gratuiti

I modelli disponibili su OpenRouter cambiano frequentemente. Per trovare sempre i migliori modelli gratuiti al momento:

#### Per OCR e analisi immagini (IMAGE_MODEL)

[Cerca modelli immagini gratuiti](https://openrouter.ai/models?input_modalities=image,text&variant=free&order=intelligence-high-to-low)

Questo link mostra tutti i modelli gratuiti che supportano **immagini + testo**, ordinati dal più intelligente al meno intelligente.

#### Per generazione testi (TEXT_MODEL)

[Cerca modelli testo gratuiti](https://openrouter.ai/models?input_modalities=text&variant=free&order=intelligence-high-to-low)

Questo link mostra tutti i modelli gratuiti che supportano **solo testo**, ordinati dal più intelligente al meno intelligente.

### Modelli consigliati

#### IMAGE_MODEL (OCR di alta qualità):

- `google/gemma-4-26b-a4b-it:free`
- `google/gemma-4-31b-it:free`

#### TEXT_MODEL (generazione testi):

- `nvidia/nemotron-3-ultra-550b-a55b:free`
