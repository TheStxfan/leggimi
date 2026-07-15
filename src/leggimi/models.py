from dataclasses import dataclass, field


@dataclass
class Page:
    num: int
    text: str


@dataclass
class Chapter:
    title: str
    pages: list[Page] = field(default_factory=list)


@dataclass
class Line:
    speaker: str
    text: str


@dataclass
class Script:
    mode: str
    lines: list[Line] = field(default_factory=list)

    @property
    def plain_text(self) -> str:
        return "\n".join(line.text for line in self.lines)
