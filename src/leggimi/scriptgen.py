from .models import Script, Line
from leggimi.config import get_openrouter_key, get_model
from leggimi.llm_client import SCRIPT_GENERATION_SYSTEM_PROMPT, _call_with_retry
from typing import Literal
from openai import (
    APIConnectionError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)
from leggimi.errors import (
    InvalidScriptFormatError,
    ModelNotFoundError,
    NoInternetConnectionError,
    ApiRequestLimitExceededError,
)


def chunk_text(
    text: str,
    max_words: int = 1500,
    overlap: int = 100,
) -> list[str]:
    """
    Divide un testo lungo in blocchi di parole sovrapposti.

    Args:
        text: Testo da dividere.
        max_words: Numero massimo di parole per blocco.
        overlap: Numero di parole ripetute tra due blocchi consecutivi.

    Returns:
        Lista dei blocchi di testo.
    """

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + max_words

        chunks.append(" ".join(words[start:end]))

        start = end - overlap

    return chunks


def _generate_chunk_script(
    chapter_text: str,
    mode: Literal["Riassunto", "Dialogo"],
    livello: Literal["base", "intermedio", "avanzato"],
    model: str,
    system_prompt: str | None,
) -> list[Line]:
    """
    Genera le battute dello script per un singolo chunk di testo.

    Args:
        chapter_text: Chunk del capitolo da rielaborare.
        mode: Modalità di generazione dello script.
        livello: Livello di complessità e approfondimento.
        model: Identificativo del modello linguistico da utilizzare.
        system_prompt: Istruzioni di sistema da fornire al modello.

    Returns:
        Lista delle battute generate.

    Raises:
        ModelNotFoundError: Se il modello linguistico configurato non è disponibile.
        NoInternetConnectionError: Se non è disponibile una connessione a Internet.
        ApiRequestLimitExceededError: Se viene superato il limite di richieste
            del provider LLM.
        InvalidScriptFormatError: Se la risposta del modello è vuota o
            non rispetta il formato previsto.
    """

    key = get_openrouter_key()

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
                {
                    "type": "text",
                    "text": (
                        f"Modalità: {mode}\n"
                        f"Livello: {livello}\n\n"
                        f"Testo del capitolo:\n{chapter_text}"
                    ),
                },
            ],
        }
    )

    for attempt in range(2):
        try:
            response = _call_with_retry(
                client=client,
                model=model,
                messages=messages,
            )

            content = response.choices[0].message.content

            if content is None:
                raise InvalidScriptFormatError(
                    "La risposta del modello è vuota.",
                )

            content_lines = []

            for line in content.splitlines():
                line = line.strip()

                if line:
                    content_lines.append(line)

            if len(content_lines) % 2 != 0:
                raise InvalidScriptFormatError(
                    "Il numero di righe della risposta non è valido.",
                )

            lines: list[Line] = []

            for i in range(0, len(content_lines), 2):
                speaker_line = content_lines[i]
                text_line = content_lines[i + 1]

                if ":" not in speaker_line or ":" not in text_line:
                    raise InvalidScriptFormatError(
                        f"Formato non valido alla battuta {i // 2 + 1}.",
                    )

                speaker_prefix, speaker = speaker_line.split(":", 1)
                text_prefix, text = text_line.split(":", 1)

                speaker_prefix = speaker_prefix.strip()
                text_prefix = text_prefix.strip()

                if speaker_prefix != "SPEAKER":
                    raise InvalidScriptFormatError(
                        f"Formato speaker non valido alla battuta {i // 2 + 1}.",
                    )

                if text_prefix != "TEXT":
                    raise InvalidScriptFormatError(
                        f"Formato testo non valido alla battuta {i // 2 + 1}.",
                    )

                speaker = speaker.strip()
                text = text.strip()

                if not speaker or not text:
                    raise InvalidScriptFormatError(
                        f"Speaker o testo vuoto alla battuta {i // 2 + 1}.",
                    )

                if speaker not in {"Speaker1", "Speaker2"}:
                    raise InvalidScriptFormatError(
                        f"Speaker non valido: {speaker}",
                    )

                if mode == "Riassunto" and speaker != "Speaker1":
                    raise InvalidScriptFormatError(
                        "In modalità 'Riassunto' è consentito solo Speaker1.",
                    )

                lines.append(
                    Line(
                        speaker=speaker,
                        text=text,
                    )
                )

            if not lines:
                raise InvalidScriptFormatError(
                    "Il modello non ha restituito alcuna battuta.",
                )

            speakers = {line.speaker for line in lines}

            if mode == "Riassunto" and speakers != {"Speaker1"}:
                raise InvalidScriptFormatError(
                    "Il riassunto deve usare esclusivamente Speaker1.",
                )

            if mode == "Dialogo" and speakers != {"Speaker1", "Speaker2"}:
                raise InvalidScriptFormatError(
                    "Il dialogo deve contenere Speaker1 e Speaker2.",
                )

            return lines

        except InvalidScriptFormatError:
            if attempt == 1:
                raise

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "La risposta precedente non rispettava il formato "
                        "richiesto. Genera nuovamente l'intero script "
                        "rispettando rigorosamente il formato obbligatorio "
                        "SPEAKER/TEXT."
                    ),
                }
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

    raise InvalidScriptFormatError(
        "Impossibile generare uno script valido dopo i tentativi disponibili.",
    )


def to_script(
    chapter_text: str,
    mode: Literal["Riassunto", "Dialogo"],
    livello: Literal["base", "intermedio", "avanzato"],
    model: str = get_model("TEXT"),
    system_prompt: str | None = SCRIPT_GENERATION_SYSTEM_PROMPT,
) -> Script:
    """
    Divide il capitolo in chunk e genera lo script per ogni parte.

    Args:
        chapter_text: Testo completo del capitolo da rielaborare.
        mode: Modalità di generazione dello script.
        livello: Livello di complessità e approfondimento.
        model: Identificativo del modello linguistico da utilizzare.
        system_prompt: Istruzioni di sistema da fornire al modello.

    Returns:
        Uno Script contenente tutte le battute generate dai vari chunk.
    """

    chunks = chunk_text(chapter_text)

    lines: list[Line] = []

    for chunk in chunks:
        lines.extend(
            _generate_chunk_script(
                chapter_text=chunk,
                mode=mode,
                livello=livello,
                model=model,
                system_prompt=system_prompt,
            )
        )

    return Script(
        mode=mode,
        lines=lines,
    )
