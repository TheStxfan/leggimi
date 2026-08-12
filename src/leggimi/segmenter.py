from .models.models import Page, Chapter
from leggimi.errors import PdfIlleggibileError, ChaptersNotFoundError


def _rimuovi_cancelletto(titolo: str) -> str:
    """
    Rimuove i caratteri '#' presenti all'inizio del titolo.

    Args:
        titolo: Titolo del capitolo da normalizzare.

    Returns:
        str: Titolo senza i caratteri '#' iniziali.
    """

    return titolo.lstrip("#").strip()


def split_chapters(pages: list[Page]) -> list[Chapter]:
    """
    Suddivide le pagine di un documento in capitoli utilizzando i titoli
    individuati nel testo.

    Args:
        pages: Lista delle pagine del documento da suddividere in capitoli.

    Returns:
        list[Chapter]: Lista dei capitoli individuati nel documento.

    Raises:
        PdfIlleggibileError: Se la lista delle pagine è vuota.
        ChaptersNotFoundError: Se non viene individuato alcun capitolo.
    """

    if not pages:
        raise PdfIlleggibileError

    chapters: list[Chapter] = []
    buffer_testo: list[str] = []
    titolo_corrente = "Introduzione"

    for page in pages:
        for line in page.text.split("\n"):
            if line.startswith("#"):
                if buffer_testo:
                    testo_completo = "\n".join(buffer_testo).strip()
                    if testo_completo:
                        chapters.append(
                            Chapter(title=titolo_corrente, text=testo_completo)
                        )
                    buffer_testo = []
                titolo_corrente = _rimuovi_cancelletto(line)
            else:
                buffer_testo.append(line)

    if buffer_testo:
        testo_completo = "\n".join(buffer_testo).strip()
        if testo_completo:
            chapters.append(Chapter(title=titolo_corrente, text=testo_completo))

    if not chapters:
        raise ChaptersNotFoundError

    return chapters
