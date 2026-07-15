import pytest
from pathlib import Path
from leggimi.extractor import extract_text


def test_extract_text_esiste():
    with pytest.raises(NotImplementedError):
        extract_text(str(Path("qualsiasi.pdf")))


def test_extract_text_file_non_esistente():
    with pytest.raises(FileNotFoundError):
        extract_text(str(Path("qualsiasi.pdf")))
