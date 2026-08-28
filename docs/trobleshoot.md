# Troubleshoot errori comuni

## Errore: "limite richieste superato"

Questo errore (codice API 429) può avere due cause principali:

### 1. Limite giornaliero del tuo account OpenRouter

OpenRouter offre **50 richieste gratuite al giorno** per gli account free.

**Verifica il tuo utilizzo:**

- Vai su [OpenRouter Activity](https://openrouter.ai/activity/explore?metric=request_count&date_preset=today&granularity=day&dimension=api_key_id)
- Controlla il numero di richieste fatte oggi
- Se hai raggiunto il limite di 50, aspetta il giorno successivo o ricarica crediti

### 2. Rate limit temporaneo del modello specifico

Anche se il tuo account non ha superato il limite, **alcuni modelli** possono essere temporaneamente limitati dal provider (es. Google AI Studio, Anthropic, ecc.).

**Soluzione:**

- **Cambia modello** nel file `.env` (consigliato)
- **Riprova più tardi** (il rate limit è temporaneo)

---

### Quale modello cambiare?

A seconda di dove compare l'errore, devi modificare una variabile diversa nel file .env:

| Dove compare l'errore              | Variabile da modificare | Link per trovare il modello migliore                                                                                              |
| :--------------------------------- | :---------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| Durante Estrazione capitoli (OCR)  | IMAGE_MODEL             | [Modelli immagine gratuiti](https://openrouter.ai/models?input_modalities=image,text&variant=free&order=intelligence-high-to-low) |
| Durante Generazione audio (script) | TEXT_MODEL              | [Modelli testo gratuiti](https://openrouter.ai/models?input_modalities=text&variant=free&order=intelligence-high-to-low)          |

> Suggerimento: Se l'errore compare subito dopo aver premuto il bottone `Estrai capitoli`, il problema è il modello che legge le immagini del PDF (IMAGE_MODEL). Se compare subito dopo aver premuto il bottone `Genera audio`, il problema è il modello che scrive il testo dello script (TEXT_MODEL).

---

### Come scegliere un modello alternativo

Se il modello che stai usando dà errore 429 (limite richieste superato) per un rate limit temporaneo, puoi trovare facilmente un'alternativa valida:

| Scopo       | Link per trovare il migliore modello gratuito                                                                                     |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------- |
| IMAGE_MODEL | [Modelli immagine gratuiti](https://openrouter.ai/models?input_modalities=image,text&variant=free&order=intelligence-high-to-low) |
| TEXT_MODEL  | [Modelli testo gratuiti](https://openrouter.ai/models?input_modalities=text&variant=free&order=intelligence-high-to-low)          |

Questi link sono pre-filtrati per mostrare solo modelli gratuiti, ordinati per intelligenza (dal migliore in alto).

**Come usare i link:**

1. Apri il link appropriato per il tuo caso
2. Scegli uno dei primi modelli
3. Copia l'ID del modello (es. `google/gemini-2.5-flash`)
4. Aggiorna il valore nel tuo file `.env`
5. Riavvia l'applicazione

---

### Errore: "modello OCR incompatibile"

Questo errore compare quando il modello scelto per l'estrazione del testo dal PDF non supporta l'OCR (ovvero non è in grado di leggere immagini).

**Cause comuni:**

- Hai scelto un modello **solo testo** (es. `nvidia/nemotron-3-ultra-550b-a55b:free`)
- Hai scelto un modello progettato per agenti di produttività (es. `thinkingmachines/inkling:free`)
- Il modello non ha il supporto per input multimodali (immagini)

**Soluzione:**

Scegli un modello differente dal [link per modelli immagini gratuiti](https://openrouter.ai/models?input_modalities=image,text&variant=free&order=intelligence-high-to-low) e aggiorna il file `.env`.

---

## Problemi comuni e soluzioni

| Errore                                           | Causa                                                  | Soluzione                                                                                   |
| ------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `limite richieste superato` (account)            | Hai superato le 50 richieste giornaliere di OpenRouter | Controlla su [OpenRouter Activity](https://openrouter.ai/activity) e aspetta il giorno dopo |
| `limite richieste superato` (provider)           | Il provider del modello ha un rate limit temporaneo    | Cambia modello nel `.env` o riprova più tardi                                               |
| `ModuleNotFoundError: No module named 'leggimi'` | Il package non è incluso nei dati                      | Lo spec file include `('src/leggimi', 'leggimi')` nei `datas`                               |
| `No module named '_cffi_backend'`                | miniaudio richiede cffi                                | Lo spec file include `_cffi_backend` negli `hiddenimports`                                  |
| `No module named 'rich'`                         | flet-desktop richiede rich                             | Lo spec file include `rich` negli `hiddenimports`                                           |
| `icons.json not found`                           | Flet non trova le icone                                | Lo spec file usa `collect_data_files('flet')` per includere tutte le risorse                |
| `OPENROUTER_API_KEY not found`                   | `.env` non viene caricato                              | Assicurati che `.env` sia nella stessa cartella dell'eseguibile                             |
| `NameError: name 'exit' is not defined`          | Bug di Flet quando manca rich                          | Includi `rich` negli `hiddenimports` (lo spec file già lo fa)                               |
| `No such file or directory: '.../icons.json'`    | Risorse di Flet mancanti                               | Usa `collect_data_files('flet')` nei `datas` (lo spec file già lo fa)                       |

# Problemi del dev environment

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

# Problemi di build

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
