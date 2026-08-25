# Compilazione con PyInstaller

Questa guida spiega come creare un eseguibile standalone di LeggiMi per Windows, macOS o Linux.

## Prerequisiti

Assicurati di aver completato la [guida all'installazione](setup.md) e che l'applicazione funzioni correttamente in modalità sviluppo.

## Installare PyInstaller

```bash
pip install pyinstaller
```

## Compilazione

### Windows

```powershell
pyinstaller --onefile --windowed --name LeggiMi --icon=icon.ico --add-data "leggimi;leggimi" --add-data ".env;." leggimi/ui/app.py
```

### Linux/macOS

```bash
pyinstaller --onefile --windowed --name LeggiMi --add-data "leggimi:leggimi" --add-data ".env:." leggimi/ui/app.py
```

## File generati

L'eseguibile si trova nella cartella `dist/`.

## Note importanti

### File `.env`

Il file `.env` deve essere presente nella stessa cartella dell'eseguibile. Non includerlo nella compilazione se contiene credenziali sensibili; forniscilo separatamente.

### Dipendenze

PyInstaller potrebbe non rilevare automaticamente tutte le dipendenze. Controlla eventuali errori nei log.

### Framework Flet

Flet richiede file aggiuntivi (font, risorse). La compilazione potrebbe richiedere di specificare esplicitamente i dati.

### Esempio di compilazione con tutte le risorse

```bash
pyinstaller --onefile --add-data "leggimi:leggimi" --add-data ".env:." --hidden-import "flet" --hidden-import "miniaudio" --hidden-import "edge_tts" --hidden-import "fitz" leggimi/ui/app.py
```
