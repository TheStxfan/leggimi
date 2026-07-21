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


def test_unisci_righe():
    assert unisci_righe("r1\nr2") == "r1 r2"
    assert unisci_righe("p1\n\np2") == "p1\n\np2"


def test_extract_text_restituisce_pagine(monkeypatch, tmp_path):
    import fitz
    from leggimi import llm_client

    pdf = tmp_path / "p.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf))
    doc.close()

    monkeypatch.setattr(
        llm_client, "get_text_from_image", lambda *a, **k: "testo pagina"
    )
    pages = extract_text(str(pdf))
    assert len(pages) == 1
    assert pages[0].num == 0
    assert pages[0].text == "testo pagina"


@pytest.mark.skipif(
    not Path("tests/fixtures/sample-pdf-columns.pdf").exists(),
    reason="Fixture PDF a tre colonne mancante",
)
def test_ordine_lettura_tre_colonne():
    risultato = extract_text("tests/fixtures/sample-pdf-columns.pdf")
    testo_completo = "".join(p.text for p in risultato)

    pos_sx = testo_completo.index("ELECTION RESULTS EDITION")
    pos_ct = testo_completo.index("Usually, politicians say")
    pos_dx = testo_completo.index("Lounge Lizard Slither")
    assert (
        pos_sx < pos_ct < pos_dx
    ), "L'ordine atteso è: colonna sinistra, poi centrale, poi destra"
