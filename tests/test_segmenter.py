from leggimi.segmenter import split_chapters
from leggimi.models import Page


def test_split_chapters_restituisce_lista():
    pages: list[Page] = []
    pages.append(
        Page(
            num=0,
            text="# Sample Doc\n\nSample Document taken from the Internet BrewPoint Volume IX, Number 12 December 1996\n\n# ELECTION RESULTS EDITION THE PEOPLE SPEAK",
        )
    )
    pages.append(
        Page(
            num=1,
            text="## Worts Just Say No!\n\nThe Boston Wort Processors once again voted against the grain and elected local representatives to positions of power over the major parties' candidates.",
        )
    )

    sezioni = split_chapters(pages)
    assert isinstance(sezioni, list)
    assert len(sezioni) == 2


def test_split_chapters_nessun_titolo():
    pages: list[Page] = []
    pages.append(
        Page(
            num=0,
            text="Sample Doc\n\nSample Document taken from the Internet BrewPoint Volume IX, Number 12 December 1996\n\nELECTION RESULTS EDITION THE PEOPLE SPEAK",
        )
    )
    sezioni = split_chapters(pages)
    assert len(sezioni) == 1
