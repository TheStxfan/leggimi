from leggimi.extractor import extract_text
from leggimi.segmenter import split_chapters
from leggimi.models import Chapter


def process_pdf(pdf_path: str) -> list[Chapter]:
    pages = extract_text(pdf_path)
    chapters = split_chapters(pages)

    return chapters
