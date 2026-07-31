"""Fondamenta: questi test devono essere VERDI da subito."""

from leggimi.models.models import Page, Chapter, Line, Script


def test_chapter_e_page():
    assert Page(num=1, text="abc").num == 1
    assert Chapter(title="Cap 1", text="...").title == "Cap 1"


def test_script_plain_text():
    s = Script(
        mode="dialogo", lines=[Line("Voce A", "Ciao"), Line("Voce B", "Come va?")]
    )
    assert s.plain_text == "Ciao\nCome va?"
