from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Page:
    num: int
    text: str


@dataclass
class Chapter:
    title: str
    text: str


@dataclass
class Line:
    speaker: str
    text: str


@dataclass
class Script:
    mode: Literal["riassunto", "dialogo"]
    lines: list[Line] = field(default_factory=list)

    @property
    def plain_text(self) -> str:
        return "\n".join(line.text for line in self.lines)
