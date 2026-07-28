import base64
import time
from openai.types.chat import ChatCompletion

from openai import (
    APIConnectionError,
    APIStatusError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)
from leggimi.config import get_openrouter_key, get_model
from leggimi.prompts import (
    TEXT_EXTRACTION_SYSTEM_PROMPT,
)
from leggimi.errors import (
    ModelNotFoundError,
    NoInternetConnectionError,
    ApiRequestLimitExceededError,
)


def _is_retryable_error(exc: Exception) -> bool:
    """
    Determina se un errore API può essere ritentato.
    """

    if isinstance(exc, (APIConnectionError, RateLimitError)):
        return True

    if isinstance(exc, APIStatusError):
        return exc.status_code == 503

    return False


def _call_with_retry(
    client: OpenAI,
    model: str,
    messages: list,
    max_retries: int = 3,
) -> ChatCompletion:
    """
    Esegue una richiesta API ritentandola in caso di errori temporanei.

    Usa un backoff esponenziale tra i tentativi.
    """

    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
            )

        except Exception as exc:
            if not _is_retryable_error(exc) or attempt == max_retries - 1:
                raise

            time.sleep(2**attempt)

    raise RuntimeError(
        "La richiesta API non ha restituito alcuna risposta.",
    )


def get_text_from_image(
    image_bytes: bytes,
    prompt: str,
    model: str = get_model("IMAGE"),
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
        system_prompt: Istruzioni di sistema da fornire al modello. Se `None`,
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

    if system_prompt is not None:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )

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
        response = _call_with_retry(
            client=client,
            model=model,
            messages=messages,
        )

    except NotFoundError as exc:
        raise ModelNotFoundError(
            f"Modello non trovato: {model}",
        ) from exc

    except APIConnectionError as exc:
        raise NoInternetConnectionError(
            "Connessione all'API fallita",
        ) from exc

    except RateLimitError as exc:
        raise ApiRequestLimitExceededError(
            "Limite richieste superato",
        ) from exc

    return response.choices[0].message.content or ""
