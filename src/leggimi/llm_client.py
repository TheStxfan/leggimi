import base64

from openai import OpenAI, NotFoundError, APIConnectionError, RateLimitError
from leggimi.config import get_openrouter_key
from leggimi.errors import (
    ModelNotFoundError,
    NoInternetConnectionError,
    ApiRequestLimitExceededError,
)

SYSTEM_PROMPT = (
    "Sei un motore OCR avanzato e strutturatore di documenti. "
    "Trascrivi il testo visibile nella pagina fornita rispettando rigorosamente l'ordine di lettura "
    "(da sinistra a destra per le colonne, dall'alto in basso).\n\n"
    "STRUTTURA E MARKDOWN:\n"
    "- Identifica i titoli di capitolo, articoli o sezioni e rappresentali ESCLUSIVAMENTE "
    "con le intestazioni Markdown (es. '# Titolo Principale', '## Sotto-sezione').\n"
    "- Non usare il grassetto '**' per le intestazioni: usa solo i simboli '#'.\n"
    "- Mantieni i paragrafi ben separati con una riga vuota.\n\n"
    "RUMORE DA ESCLUDERE (IMPORTANTE):\n"
    "- IGNORA ed ELIMINA completamente: numeri di pagina, intestazioni di pagina ripetitive (header), "
    "piè di pagina (footer), note di margine con numeri di volume/data (es. 'Volume IX, Number 12') "
    "e riferimenti di impaginazione (es. 'President's Letter, page 2').\n"
    "- Non aggiungere commenti o introduzioni (es. 'Ecco il testo').\n\n"
    "TESTO ED ERRORI:\n"
    "- Trascrivi fedelmente il corpo del testo senza tradurre o riassumere.\n"
    "- Se una parola è spezzata da un trattino a fine riga, lasciala così (es. 'trat-\\nto')."
)


def get_text_from_image(
    image_bytes: bytes,
    prompt: str,
    model: str = "google/gemma-4-26b-a4b-it:free",  # alternative: google/gemma-4-31b-it:free
    system_prompt: str | None = SYSTEM_PROMPT,
) -> str:
    """
    Completa il prompt utilizzando un modello di linguaggio.

    Args:
        image_bytes: l'immagine della pagina.
        prompt: il prompt da completare.
        model: modello openrouter da usare.
        system_prompt: prompt di sistema del modello.

    Returns:
        La stringa contenente il testo estratto dall'immagine della pagina.

    Raises:
        ModelNotFoundError: se il modello non è stato trovato.
        NoInternetConnectionError: se non c'è connessione a internet.
        ApiRequestLimitExceededError: se il limite di richieste all'API è stato superato.
    """
    # raise NotImplementedError

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
