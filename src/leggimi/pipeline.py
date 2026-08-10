import asyncio
from pathlib import Path

from typing_extensions import Literal

from leggimi.extractor import extract_text
from leggimi.segmenter import split_chapters
from leggimi.scriptgen import to_script
from leggimi.models.models import Chapter, Page, Script, Line
from leggimi.tts import synthesize_script


def process_pdf(pdf_path: str) -> list[Chapter]:
    """
    Elabora un documento PDF estraendo il testo e suddividendolo in capitoli.

    Args:
        pdf_path: Percorso del file PDF da elaborare.

    Returns:
        list[Chapter]: Lista dei capitoli estratti dal documento.
    """

    pages = extract_text(pdf_path)

    chapters = split_chapters(pages)

    return chapters


def generate_chapter_script(
    chapter: Chapter,
    mode: Literal["riassunto", "dialogo"],
    livello: Literal["base", "intermedio", "avanzato"],
) -> Script:
    """
    Genera uno script a partire dal contenuto di un capitolo.

    Lo script viene generato in modalità riassunto o dialogo, in base alla
    modalità e al livello di elaborazione specificati.

    Args:
        chapter: Capitolo da cui generare lo script.
        mode: Modalità di generazione dello script, tra riassunto e dialogo.
        livello: Livello di elaborazione dello script, tra base, intermedio
            e avanzato.

    Returns:
        Script: Script generato a partire dal capitolo.
    """

    return to_script(
        chapter.text,
        mode,
        livello,
    )


async def generate_chapter_audio(
    pdf_name: str,
    chapter: Chapter,
    mode: Literal["riassunto", "dialogo"],
    livello: Literal["base", "intermedio", "avanzato"],
) -> None:
    """
    Genera lo script, l'audio e i sottotitoli di un capitolo.

    Args:
        pdf_name: Nome del file PDF sorgente senza estensione.
        chapter: Capitolo da convertire in audio.
        mode: Modalità di generazione dello script.
        livello: Livello di elaborazione dello script.

    Returns:
        None
    """

    output_name = f"{pdf_name}_{chapter.title}_{mode}_{livello}".replace(" ", "_")

    output_mp3 = Path("./output") / f"{output_name}.mp3"
    output_srt = Path("./output") / f"{output_name}.srt"

    if output_mp3.exists() and output_srt.exists():
        return

    if output_mp3.exists():
        output_mp3.unlink()

    if output_srt.exists():
        output_srt.unlink()

    script = await asyncio.to_thread(
        generate_chapter_script,
        chapter,
        mode,
        livello,
    )

    await synthesize_script(
        script,
        output_name,
    )
