# Compilazione con PyInstaller

Questa guida spiega come creare un eseguibile standalone di LeggiMi per Windows, macOS o Linux.

## Prerequisiti

Assicurati di aver completato la [guida all'installazione](setup.md) e che l'applicazione funzioni correttamente in modalità sviluppo.

> **Piattaforma supportata**: La compilazione è testata e funzionante **solo su Linux**. La procedura per Windows e macOS non è attualmente supportata e potrebbe richiedere modifiche significative allo spec file e alle dipendenze.

## Installare PyInstaller

```bash
pip install pyinstaller
```

## Compilazione con lo spec file

Nella root del progetto è presente il file `leggimi.spec` che contiene tutte le configurazioni necessarie per la compilazione.

```bash
pyinstaller leggimi.spec --clean

```

L'eseguibile verrà creato in `dist/`.

## File generati

```
dist/
├── LeggiMi # Eseguibile
├── .env # Configurazione (fornito separatamente)
├── output/ # Creato automaticamente (file MP3 e SRT)
├── cache/ # Creato automaticamente (capitoli estratti)
└── temp/ # Creato automaticamente (file temporanei)
```

## Note importanti

### File .env

Il file `.env` deve essere presente nella stessa cartella dell'eseguibile. Non viene incluso nella compilazione per ragioni di sicurezza; deve essere fornito separatamente dall'utente.

Vedi come configurare l'env [qui](setup.md).

## Portabilità

L'eseguibile è completamente portatile: puoi spostare LeggiMi in qualsiasi cartella e funzionerà, purché il .env sia nella stessa cartella.

## Ricostruire dopo modifiche al codice

Se modifichi il codice sorgente, ricostruisci semplicemente:

```bash
pyinstaller leggimi.spec --clean
```
