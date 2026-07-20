import pytest
from pathlib import Path
from leggimi.extractor import (
    extract_text,
    rimuovi_sillabazione,
    unisci_righe,
)


def test_file_non_esistente():
    with pytest.raises(FileNotFoundError):
        extract_text("qualsiasi.pdf")


def test_rimuovi_sillabazione():
    assert rimuovi_sillabazione("trat-\nto") == "tratto"
    assert rimuovi_sillabazione("ca-\nsa") == "casa"


def test_unisci_righe():
    assert unisci_righe("riga1\nriga2") == "riga1 riga2"
    assert unisci_righe("par1\n\npar2") == "par1\n\npar2"


def test_extract_text_restituisce_pagine(monkeypatch, tmp_path):
    import fitz
    from leggimi import llm_client

    pdf = tmp_path / "p.pdf"
    with fitz.open() as doc:
        doc.new_page()
        doc.save(str(pdf))

    monkeypatch.setattr(
        llm_client, "get_text_from_image", lambda *a, **k: "testo pagina"
    )

    pages = extract_text(str(pdf))

    assert len(pages) == 1
    assert pages[0].num == 0
    assert pages[0].text == "testo pagina"
