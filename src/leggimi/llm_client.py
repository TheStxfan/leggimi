import base64
from typing import Literal

from openai import OpenAI, NotFoundError, APIConnectionError, RateLimitError
from leggimi.config import get_openrouter_key
from leggimi.errors import (
    ModelNotFoundError,
    NoInternetConnectionError,
    ApiRequestLimitExceededError,
)
from leggimi.models import Script

TEXT_EXTRACTION_SYSTEM_PROMPT = """
Sei un motore OCR avanzato e strutturatore di documenti.

OBIETTIVO:
Trascrivi fedelmente il testo visibile nella pagina fornita, rispettando
rigorosamente l'ordine di lettura naturale del documento.

ORDINE DI LETTURA:
- Leggi dall'alto verso il basso.
- In presenza di più colonne, leggi da sinistra a destra.
- Rispetta l'ordine logico dei contenuti della pagina.

STRUTTURA E MARKDOWN:
- Identifica i titoli di capitolo, articoli o sezioni e rappresentali
  ESCLUSIVAMENTE con intestazioni Markdown (es. "# Titolo Principale",
  "## Sotto-sezione").
- Non usare il grassetto "**" per le intestazioni: usa solo i simboli "#".
- Mantieni i paragrafi ben separati con una riga vuota.

RUMORE DA ESCLUDERE (IMPORTANTE):
- IGNORA ed ELIMINA completamente i numeri di pagina.
- IGNORA ed ELIMINA le intestazioni di pagina ripetitive (header).
- IGNORA ed ELIMINA i piè di pagina (footer).
- IGNORA ed ELIMINA le note di margine con numeri di volume/data
  (es. "Volume IX, Number 12").
- IGNORA ed ELIMINA i riferimenti di impaginazione
  (es. "President's Letter, page 2").

TESTO ED ERRORI:
- Trascrivi fedelmente il corpo del testo senza tradurre o riassumere.
- Se una parola è spezzata da un trattino a fine riga, lasciala così
  (es. "trat-\\nto").
- Non aggiungere commenti o introduzioni
  (es. "Ecco il testo").
"""

SCRIPT_GENERATION_SYSTEM_PROMPT = """
Sei un tutor esperto nella trasformazione di testi scolastici
in contenuti chiari e facili da ascoltare.

DESTINATARIO:
Il contenuto è destinato principalmente a studenti delle scuole superiori.
Deve essere accessibile anche a studenti con DSA o BES e difficoltà di lettura
o comprensione.

OBIETTIVO:
Trasforma il testo fornito in uno script audio naturale, chiaro e coinvolgente.
Non limitarti a leggere o copiare il testo originale: rielaboralo per l'ascolto.

CONTENUTO:
- Mantieni fedelmente i concetti fondamentali del testo originale.
- Non inventare informazioni.
- Non contraddire il testo originale.
- Non eliminare definizioni, date, formule, nomi o relazioni importanti.
- Semplifica il linguaggio senza alterare il significato.
- Spiega i termini tecnici quando necessario.
- Usa esempi concreti per chiarire i concetti astratti o difficili.
- Organizza la spiegazione in un ordine logico e progressivo.

STILE PER L'ASCOLTO:
- Usa un linguaggio naturale, come in una spiegazione orale.
- Preferisci frasi brevi e chiare.
- Evita periodi eccessivamente complessi.
- Usa transizioni naturali tra gli argomenti.
- Evita elenchi troppo lunghi quando una spiegazione discorsiva è più naturale.
- Mantieni un tono amichevole, chiaro e incoraggiante.
- Non usare emoji.
- Non aggiungere introduzioni o commenti sul processo di generazione.

MODALITÀ:
La modalità richiesta determina la struttura dello script.

Se la modalità è "Riassunto":
- Usa un solo speaker.
- Crea una spiegazione discorsiva e coerente.
- Dai priorità alla chiarezza e ai concetti fondamentali.

Se la modalità è "Dialogo":
- Usa due speaker distinti.
- Il primo speaker presenta e spiega i concetti.
- Il secondo speaker pone domande, chiede chiarimenti o propone esempi.
- Il dialogo deve sembrare naturale e contribuire alla comprensione.
- Evita domande artificiali o ripetitive.
- Entrambi gli speaker devono contribuire alla spiegazione.

LIVELLO:
Il livello richiesto determina la profondità e la complessità della spiegazione.

Livello "base":
- Usa un linguaggio molto semplice.
- Spiega i termini tecnici con parole comuni.
- Usa esempi frequenti.
- Procedi gradualmente e riprendi i concetti fondamentali quando necessario.

Livello "intermedio":
- Usa un linguaggio semplice ma preciso.
- Mantieni la terminologia tecnica essenziale.
- Spiega i concetti più complessi con esempi quando utile.

Livello "avanzato":
- Mantieni una terminologia più tecnica e precisa.
- Riduci le semplificazioni non necessarie.
- Privilegia completezza e accuratezza.

FORMATO DELL'OUTPUT:
Restituisci esclusivamente lo script richiesto.
Non aggiungere spiegazioni, commenti o testo al di fuori dello script.
"""


def get_text_from_image(
    image_bytes: bytes,
    prompt: str,
    model: str = "google/gemma-4-26b-a4b-it:free",  # alternative: google/gemma-4-31b-it:free
    system_prompt: str | None = TEXT_EXTRACTION_SYSTEM_PROMPT,
) -> str:
    """
    Estrae il testo visibile da un'immagine di una pagina.

    Il testo viene trascritto da un modello multimodale rispettando l'ordine
    di lettura della pagina. Il modello restituisce il contenuto testuale
    strutturato in Markdown, escludendo gli elementi di rumore specificati
    dal system prompt.

    Args:
        image_bytes: Contenuto binario dell'immagine della pagina da analizzare.
        prompt: Istruzioni aggiuntive per il modello relative all'estrazione.
        model: Identificativo del modello multimodale da utilizzare.
        system_prompt: Istruzioni di sistema da fornire al modello. Se ``None``,
            non viene utilizzato alcun system prompt.

    Returns:
        Il testo estratto dall'immagine, strutturato secondo le istruzioni
        fornite al modello.

    Raises:
        ModelNotFoundError: Se il modello specificato non è disponibile.
        NoInternetConnectionError: Se non è possibile stabilire una connessione
            con il provider.
        ApiRequestLimitExceededError: Se viene superato il limite di richieste
            imposto dal provider.
    """

    key = get_openrouter_key()
    b64 = base64.b64encode(image_bytes).decode()
    data_url = f"data:image/png;base64,{b64}"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
    )

    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except NotFoundError as exc:
        raise ModelNotFoundError(f"Modello non trovato: {model}") from exc

    except APIConnectionError as exc:
        raise NoInternetConnectionError("Connessione all'API fallita") from exc

    except RateLimitError as exc:
        raise ApiRequestLimitExceededError("Limite richieste superato") from exc

    return response.choices[0].message.content or ""


def to_script(
    chapter_text: str,
    mode: Literal["Riassunto", "Dialogo"],
    livello: Literal["base", "intermedio", "avanzato"],
) -> Script:
    """
    Trasforma il testo di un capitolo scolastico in uno script ottimizzato
    per l'ascolto.

    Il contenuto viene rielaborato secondo la modalità richiesta:

    - ``"Riassunto"``: una spiegazione discorsiva e coerente con un solo speaker;
    - ``"Dialogo"``: una spiegazione sotto forma di dialogo tra due speaker.

    Il livello determina la profondità e la complessità della spiegazione:

    - ``"base"``: linguaggio molto semplice, spiegazioni graduali ed esempi frequenti;
    - ``"intermedio"``: linguaggio semplice ma preciso, con terminologia tecnica
      essenziale;
    - ``"avanzato"``: maggiore precisione e completezza, con terminologia più tecnica.

    Args:
        chapter_text: Testo del capitolo scolastico da rielaborare.
        mode: Modalità di generazione dello script.
        livello: Livello di complessità e approfondimento della spiegazione.

    Returns:
        Uno ``Script`` contenente la modalità utilizzata e la lista ordinata
        delle battute da convertire successivamente in audio.

    Raises:
        ModelNotFoundError: Se il modello linguistico configurato non è disponibile.
        NoInternetConnectionError: Se non è disponibile una connessione a Internet.
        ApiRequestLimitExceededError: Se viene superato il limite di richieste
            del provider LLM.
    """
    raise NotImplementedError
