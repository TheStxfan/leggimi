# Struttura del progetto

```
leggimi/
├── src/                            # Codice sorgente
│   └── leggimi/
│       ├── models/
│       │   ├── app_state.py        # Stato dell'applicazione
│       │   └── models.py
│       ├── ui/                     # Interfaccia grafica
│       │   ├── app.py              # Punto di ingresso dell'interfaccia
│       │   ├── playback_lines.py   # Visualizzazione sottotitoli
│       │   ├── ui_components.py    # Componenti UI riutilizzabili
│       │   ├── ui_config.py        # Configurazioni UI
│       │   └── ui_theme.py         # Gestione temi
│       ├── __init__.py
│       ├── audio_player.py         # Riproduzione audio MP3/SRT
│       ├── cache.py                # Cache capitoli su disco
│       ├── config.py               # Configurazioni e variabili d'ambiente
│       ├── errors.py               # Gerarchia eccezioni personalizzate
│       ├── extractor.py            # Estrazione testo da PDF
│       ├── llm_client.py           # Client API OpenRouter
│       ├── pipeline.py             # Pipeline principale
│       ├── prompts.py              # Prompt per modelli IA
│       ├── scriptgen.py            # Generazione script audio
│       ├── segmenter.py            # Suddivisione capitoli
│       └── tts.py                  # Sintesi vocale (Edge TTS)
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_extractor.py
│   ├── test_models.py
│   ├── test_scriptgen.py
│   └── test_segmenter.py
├── .venv/                          # Ambiente virtuale
├── .env                            # Configurazione (creato da .env.example)
├── main.py                         # Punto di ingresso
└── requirements.txt                # Dipendenze
```

## Output generati

Durante l'uso, i file audio e sottotitoli vengono salvati in:

```
output/
├── nome_pdf_titolo_capitolo_modalita_livello.mp3
└── nome_pdf_titolo_capitolo_modalita_livello.srt
```

I capitoli estratti vengono salvati in cache:

```
cache/
└── chapters/
    └── <hash>.json
```
