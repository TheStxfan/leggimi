# Risoluzione problemi del dev environment

## Errore: "OPENROUTER_API_KEY not found" in sviluppo

Assicurati che il file `.env` esista nella **root del progetto** (dove c'è `main.py`) e contenga la chiave API.

```bash
# Verifica che il file esista
ls -la .env

# Se non esiste, copialo da .env.example
cp .env.example .env
```

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

## Piattaforme supportate

Questa applicazione è attualmente **testata e sviluppata solo su Linux**. Le build per Windows e macOS potrebbero funzionare con modifiche allo spec file, ma non sono supportate attivamente.

## L'eseguibile non parte

- **Verifica che `.env` sia presente nella stessa cartella dell'eseguibile**
- Controlla i permessi di esecuzione
- Esegui da terminale per vedere i messaggi di errore:

```bash
./dist/LeggiMi
```

## Problemi di import durante la compilazione

Usa lo spec file `leggimi.spec` per la compilazione, che include automaticamente tutte le dipendenze necessarie:

```bash
pyinstaller leggimi.spec --clean
```

## Problemi comuni e soluzioni

| Errore                                           | Causa                             | Soluzione                                                                    |
| ------------------------------------------------ | --------------------------------- | ---------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'leggimi'` | Il package non è incluso nei dati | Lo spec file include `('src/leggimi', 'leggimi')` nei `datas`                |
| `No module named '_cffi_backend'`                | miniaudio richiede cffi           | Lo spec file include `_cffi_backend` negli `hiddenimports`                   |
| `No module named 'rich'`                         | flet-desktop richiede rich        | Lo spec file include `rich` negli `hiddenimports`                            |
| `icons.json not found`                           | Flet non trova le icone           | Lo spec file usa `collect_data_files('flet')` per includere tutte le risorse |
| `OPENROUTER_API_KEY not found`                   | `.env` non viene caricato         | Assicurati che `.env` sia nella stessa cartella dell'eseguibile              |
| `NameError: name 'exit' is not defined`          | Bug di Flet quando manca rich     | Includi `rich` negli `hiddenimports` (lo spec file già lo fa)                |
| `No such file or directory: '.../icons.json'`    | Risorse di Flet mancanti          | Usa `collect_data_files('flet')` nei `datas` (lo spec file già lo fa)        |

## DLL mancanti (Windows)

Se su Windows ottieni errori relativi a DLL mancanti, installa i runtime Visual C++ ridistribuibili:

- [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

## Ricostruire dopo modifiche al codice

Se modifichi il codice sorgente, ricostruisci con:

```bash
pyinstaller leggimi.spec --clean
```

## Portabilità dell'eseguibile

L'eseguibile è completamente portatile: puoi spostare `LeggiMi` in qualsiasi cartella e funzionerà, purché:

1. Il file `.env` sia nella stessa cartella
2. L'eseguibile abbia i permessi di esecuzione

```bash
# Esempio: spostare l'eseguibile in Downloads
mv dist/LeggiMi ~/Downloads/
cp .env ~/Downloads/
cd ~/Downloads/
./LeggiMi
```

---

## `.env.example`

Copia questo file come `.env` e compila i valori:

```env
# Chiave API per OpenRouter (obbligatoria)
OPENROUTER_API_KEY=sk-or-v1-...

# Modello per l'estrazione del testo dalle immagini PDF
IMAGE_MODEL=google/gemma-4-26b-a4b-it:free

# Modello per la generazione degli script
TEXT_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
```

---

## Riepilogo delle modifiche

| Sezione                          | Modifica                                                     |
| :------------------------------- | :----------------------------------------------------------- |
| **Errore `OPENROUTER_API_KEY`**  | Specifica che il `.env` deve stare nella root del progetto   |
| **L'eseguibile non parte**       | Aggiunto comando per eseguire da terminale e vedere l'errore |
| **Il `.env` non viene caricato** | Sezione dedicata con spiegazione chiara                      |
| **Problemi di import**           | Spiegazione sull'uso dello spec file                         |
| **Tabella problemi comuni**      | Aggiunti tutti gli errori riscontrati con le soluzioni       |
| **Portabilità**                  | Spiegazione su come spostare l'eseguibile                    |
| **Verifica rapida**              | Messaggi di debug per verificare il caricamento del `.env`   |
