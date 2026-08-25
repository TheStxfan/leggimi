# Risoluzione problemi di environment di sviluppo

## Errore: "OPENROUTER_API_KEY not found"

Assicurati che il file `.env` esista e contenga la chiave API.

## Errore: "ModuleNotFoundError"

Verifica che l'ambiente virtuale sia attivo e che tutte le dipendenze siano installate:

```bash
pip install -r requirements.txt
```

## Errore: "No module named 'leggimi'"

Assicurati di eseguire il comando dalla directory principale del progetto (dove si trova `main.py`) o imposta `PYTHONPATH`:

### Linux/macOS

```bash
export PYTHONPATH="${PWD}/src:${PYTHONPATH:-}"
```

### Windows

```powershell
set PYTHONPATH="%CD%\src;%PYTHONPATH%"
```

---

# Risoluzione problemi di build

## L'eseguibile non parte

- Verifica che `.env` sia presente nella stessa cartella
- Controlla i permessi di esecuzione
- Esegui da terminale per vedere i messaggi di errore

## Errori di import

Aggiungi --hidden-import per i moduli mancanti.

## DLL mancanti (Windows)

Installa i runtime Visual C++ ridistribuibili.

## `.env.example`

Copia questo file come .env e compila i valori

```env
# Chiave API per OpenRouter (obbligatoria)
OPENROUTER_API_KEY=sk-or-v1-...

# Modello per l'estrazione del testo dalle immagini PDF
IMAGE_MODEL=google/gemma-4-26b-a4b-it:free

# Modello per la generazione degli script
TEXT_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
```
