import fitz
import re

from pathlib import Path
from leggimi import llm_client
from leggimi.errors import LeggiMiError
from .models import Page


def extract_text(pdf_path: str) -> list[Page]:
    """
    Estrae il testo grezzo dal PDF, una stringa per pagina.

    Args:
        pdf_path: percorso al file PDF.

    Returns:
        Lista di oggetti Page, uno per pagina.

    Raises:
        FileNotFoundError: se il file non esiste.
    """

    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"Il file PDF non esiste: {pdf_path}")

    pages: list[Page] = []
    with fitz.open(pdf_path) as doc:
        for idx, page in enumerate(doc):  # type: ignore
            try:
                text = estrai_pagina_ordinata(idx, page)
            except LeggiMiError:
                raise
            except Exception:
                text = ""
            pages.append(Page(num=idx, text=text))

    return pages


def estrai_pagina_ordinata(idx: int, page) -> str:
    """
    Estrae il testo ordinato da una singola pagina del PDF

    Args:
        idx: indice della pagina.
        page: oggetto pagina PyMuPDF da trascrivere.

    Returns:
        Testo della pagina

    Raises:
        RuntimeError: se l'estrazione o la trascrizione della pagina fallisce.
    """

    try:
        page_img = page.get_pixmap(dpi=200)
        img_bytes = page_img.tobytes("png")

        raw_text = llm_client.get_text_from_image(
            img_bytes,
            prompt="Trascrivi tutto il testo visibile in questa pagina, mantenendo la struttura dei paragrafi.",
            system_prompt=llm_client.SYSTEM_PROMPT,
        )

        text = rimuovi_sillabazione(raw_text)
        text = unisci_righe(text)

    except LeggiMiError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Errore durante l'elaborazione della pagina {idx}") from exc

    return text


def rimuovi_sillabazione(testo: str) -> str:
    """
    Rimuove la sillabazione a fine riga.

    Raises:
        TypeError: se `testo` non è una stringa.
    """

    return re.sub(r"-\n(\S)", r"\1", testo)


def unisci_righe(testo: str) -> str:
    """
    Unisce le righe consecutive mantenendo separati i paragrafi.

    Raises:
        TypeError: se `testo` non è una stringa.
    """

    return re.sub(r"(?<!\n)\n(?!\n)", " ", testo)
