from .models.models import Page, Chapter
from leggimi.errors import PdfIlleggibileError, ChaptersNotFoundError


def split_chapters(pages: list[Page]) -> list[Chapter]:
    """
    Divide le pagine in capitoli basandosi sui titoli.

    Args:
        pages: Lista di oggetti Page.

    Returns:
        Lista di oggetti Chapter.

    Raises:
        ChaptersNotFoundError: se i capitoli non esistono.
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
                titolo_corrente = line.lstrip("# ").strip()
            else:
                buffer_testo.append(line)

    if buffer_testo:
        testo_completo = "\n".join(buffer_testo).strip()
        if testo_completo:
            chapters.append(Chapter(title=titolo_corrente, text=testo_completo))

    if not chapters:
        raise ChaptersNotFoundError

    return chapters
