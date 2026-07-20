import base64

from openai import OpenAI
from leggimi.config import get_openrouter_key

SYSTEM_PROMPT = (
    "Sei un motore OCR ad alta precisione. "
    "Trascrivi ESATTAMENTE il testo visibile nella pagina fornita, "
    "senza tradurre, riassumere, commentare o aggiungere contenuti. "
    "Mantieni la struttura originale: lascia un ritorno a capo alla fine di "
    "ogni riga e una riga vuota tra un paragrafo e l'altro. "
    "Conserva titoli, intestazioni e la punteggiatura originale. "
    "Se una parola è spezzata da un trattino a fine riga, lasciala così "
    "(es. 'trat-\\nto'): verrà ricomposta in un secondo momento. "
    "Non includere note del tipo 'Ecco il testo'."
)


def get_text_from_image(
    image_bytes: bytes,
    prompt: str,
    model: str = "google/gemma-4-26b-a4b-it:free",  # alternative: google/gemma-4-31b-it:free
    system_prompt: str | None = None,
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
        NotImplementedError: implementazione non ancora disponibile.
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

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content or ""
