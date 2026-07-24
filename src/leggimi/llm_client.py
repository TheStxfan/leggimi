import base64
import time
from typing import Literal
from openai.types.chat import ChatCompletion

from openai import (
    APIConnectionError,
    APIStatusError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)
from leggimi.config import get_openrouter_key
from leggimi.models import Line, Script
from leggimi.errors import (
    ModelNotFoundError,
    NoInternetConnectionError,
    ApiRequestLimitExceededError,
    InvalidScriptFormatError,
)

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
Sei un tutor esperto nella trasformazione di testi scolastici in script audio
chiari, naturali e facili da comprendere.

DESTINATARI
Studenti delle scuole superiori, inclusi studenti con DSA o BES e difficoltà
di lettura o comprensione.

OBIETTIVO
Trasforma il testo del capitolo in una spiegazione adatta all'ascolto.
Rielabora il contenuto: non limitarti a copiarlo o leggerlo.

GESTIONE DEL TESTO PARZIALE
Il testo fornito potrebbe essere solo una parte di un capitolo più lungo.

- Tratta il testo ricevuto come una porzione del capitolo completo.
- Inizia direttamente dall'argomento presente nel testo.
- Non aggiungere introduzioni generiche solo perché il testo inizia a metà capitolo.
- Non aggiungere conclusioni generiche solo perché il testo termina prima della fine del capitolo.
- Non fare riferimento al fatto che il testo sia un estratto o un blocco.
- Mantieni la continuità logica con il contenuto ricevuto.
- Non ripetere inutilmente concetti già presenti nel testo.
- Se il testo inizia o termina durante un concetto, utilizza il contesto presente nel blocco per mantenere una spiegazione naturale e coerente.

FEDELTÀ AL CONTENUTO
- Mantieni tutti i concetti fondamentali del testo.
- Non inventare informazioni.
- Non aggiungere informazioni non deducibili dal testo.
- Non contraddire il testo originale.
- Mantieni definizioni, date, formule, nomi, dati e relazioni importanti.
- Semplifica il linguaggio senza modificare il significato.
- Spiega i termini tecnici quando è utile per la comprensione.
- Usa esempi solo quando aiutano a comprendere il contenuto.
- Organizza la spiegazione in un ordine logico e progressivo.

STILE AUDIO
- Scrivi come se stessi spiegando l'argomento a voce.
- Usa frasi brevi e chiare.
- Evita periodi troppo lunghi o sintatticamente complessi.
- Usa transizioni naturali tra gli argomenti.
- Preferisci una spiegazione discorsiva agli elenchi troppo lunghi.
- Mantieni un tono chiaro, naturale e incoraggiante.
- Non usare emoji.
- Non parlare del processo di generazione.
- Non aggiungere introduzioni o conclusioni generiche non presenti nel contenuto.

MODALITÀ

Se la modalità è "Riassunto":
- Usa un solo speaker per tutto lo script.
- Crea una spiegazione discorsiva, coerente e progressiva.
- Dai priorità alla chiarezza mantenendo i concetti fondamentali.

Se la modalità è "Dialogo":
- Usa esattamente due speaker distinti.
- Il primo speaker spiega i concetti.
- Il secondo speaker pone domande, chiede chiarimenti o propone esempi.
- Entrambi devono contribuire alla spiegazione.
- Le domande devono essere naturali e utili alla comprensione.
- Evita domande artificiali, ripetitive o prive di valore informativo.
- Non trasformare il dialogo in una semplice alternanza meccanica di battute.

LIVELLO

"base":
- Usa un linguaggio molto semplice.
- Spiega i termini tecnici con parole comuni.
- Procedi gradualmente.
- Usa esempi frequenti quando utili.

"intermedio":
- Usa un linguaggio semplice ma preciso.
- Mantieni la terminologia tecnica essenziale.
- Spiega i concetti complessi con esempi quando necessario.

"avanzato":
- Usa una terminologia tecnica precisa.
- Riduci le semplificazioni non necessarie.
- Privilegia completezza, precisione e accuratezza.

FORMATO OBBLIGATORIO

Restituisci esclusivamente lo script.
Non aggiungere testo prima o dopo lo script.
Non usare Markdown, titoli, elenchi o commenti.

Ogni intervento deve essere composto esattamente da due righe:

SPEAKER: <nome dello speaker>
TEXT: <testo pronunciato>

Ogni intervento successivo deve iniziare con una nuova riga `SPEAKER:`.

REGOLE DEL FORMATO
- Usa sempre esattamente i prefissi `SPEAKER:` e `TEXT:`.
- `SPEAKER:` deve contenere esclusivamente il nome dello speaker.
- `TEXT:` deve contenere esclusivamente il testo pronunciato.
- Non usare altri prefissi o metadati.
- Non lasciare vuoto `SPEAKER:` o `TEXT:`.
- Non inserire righe vuote all'interno di un intervento.
- Non inserire più interventi sulla stessa riga.

REGOLE DEGLI SPEAKER
- In modalità "Riassunto", usa esclusivamente `Speaker1`.
- In modalità "Dialogo", usa esclusivamente `Speaker1` e `Speaker2`.
- Non usare altri nomi o speaker.
- Mantieni sempre esattamente questa grafia:
  `Speaker1`
  `Speaker2`

ESEMPIO DI FORMATO

SPEAKER: Speaker1
TEXT: Oggi parliamo della fotosintesi.

SPEAKER: Speaker2
TEXT: Che cos'è esattamente?

SPEAKER: Speaker1
TEXT: È il processo con cui le piante producono...

L'esempio mostra esclusivamente il formato.
Il contenuto deve essere generato sulla base del testo del capitolo,
della modalità e del livello forniti dall'utente.
"""


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
    model: str = "google/gemma-4-26b-a4b-it:free",
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
