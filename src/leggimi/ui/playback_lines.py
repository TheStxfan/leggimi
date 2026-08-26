# playback_lines.py
from dataclasses import dataclass, field
from pathlib import Path
import bisect

import flet as ft

from leggimi.tts import _timestamp_to_seconds


@dataclass
class PlaybackLines:
    """
    Gestisce la visualizzazione delle righe SRT nella schermata di riproduzione.
    """

    srt_path: Path
    ui_size: float
    text_color: str
    background_color: str

    current_line: int = field(default=0, init=False)
    lines: list[str] = field(default_factory=list, init=False)
    timestamps: list[float] = field(default_factory=list, init=False)
    _last_scrolled_line: int = field(default=0, init=False, repr=False)
    text_controls: list[ft.Container] = field(
        default_factory=list,
        init=False,
        repr=False,
    )
    column: ft.Column = field(init=False)
    container: ft.Container = field(init=False)

    def __post_init__(self) -> None:
        """
        Inizializza il container e carica il file SRT.
        """
        self.column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.container = ft.Container(
            expand=True,
            padding=ft.Padding.only(
                left=30,
                right=30,
                top=20,
                bottom=20,
            ),
            content=self.column,
        )
        self._load_srt()

    def _load_srt(self) -> None:
        """
        Carica il testo e i timestamp delle righe dal file SRT.
        """
        content = self.srt_path.read_text(encoding="utf-8")
        blocks = content.strip().split("\n\n")

        for block in blocks:
            block_lines = block.splitlines()
            if len(block_lines) < 3:
                continue

            timestamp_str = block_lines[1].split(" --> ")[0]
            self.timestamps.append(_timestamp_to_seconds(timestamp_str))

            text = " ".join(block_lines[2:]).strip()
            if text:
                self.lines.append(text)

        self._build_controls()

    def _build_controls(self) -> None:
        """
        Crea i controlli grafici delle righe SRT.
        """
        self.column.controls.clear()
        self.text_controls.clear()
        self._last_scrolled_line = 0

        for index, text in enumerate(self.lines):
            text_control = ft.Text(
                value=text,
                size=self.ui_size,
                color=self.text_color,
                weight=(
                    ft.FontWeight.BOLD
                    if index == self.current_line
                    else ft.FontWeight.NORMAL
                ),
                text_align=ft.TextAlign.CENTER,
            )

            line_container = ft.Container(
                key=f"line_{index}",
                content=text_control,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                border_radius=45,
                bgcolor=self.background_color if index == self.current_line else None,
            )

            self.text_controls.append(line_container)
            self.column.controls.append(line_container)

    def get_line_at_timestamp(self, seconds: float) -> int:
        """
        Restituisce l'indice della linea in base al timestamp corrente.
        """
        if not self.timestamps:
            return 0

        idx = bisect.bisect_right(self.timestamps, seconds) - 1
        return max(0, min(idx, len(self.lines) - 1))

    async def scroll_to_line(self, line_index: int, duration: int = 300) -> None:
        """
        Scorre il contenitore per mostrare la linea specificata con animazione.
        Prima e ultima riga usano un offset esatto (0 e -1, garantiti da Flet
        stesso, non stimati). Le righe intermedie scorrono in modo relativo
        (delta) rispetto all'ultima posizione nota: il limite reale dello
        scroll è gestito direttamente da Flet/Flutter, non da una stima
        nostra, quindi non può più bloccarsi prima di arrivare a destinazione.
        """
        if not self.text_controls or line_index >= len(self.text_controls):
            return

        last_index = len(self.lines) - 1

        if line_index == 0:
            await self.column.scroll_to(
                offset=0,
                duration=duration,
                curve=ft.AnimationCurve.EASE_IN_OUT,
            )
        elif line_index == last_index:
            await self.column.scroll_to(
                offset=-1,
                duration=duration,
                curve=ft.AnimationCurve.EASE_IN_OUT,
            )
        else:
            spacing = self.column.spacing or 0
            line_height = self.ui_size * 4.5
            delta = (line_index - self._last_scrolled_line) * (line_height + spacing)

            await self.column.scroll_to(
                delta=delta,
                duration=duration,
                curve=ft.AnimationCurve.EASE_IN_OUT,
            )

        self._last_scrolled_line = line_index

    def update_current_line(self, line_index: int) -> None:
        """
        Aggiorna la riga attualmente selezionata.
        """
        if not self.lines or line_index == self.current_line:
            return

        self.current_line = max(0, min(line_index, len(self.lines) - 1))

        for index, container in enumerate(self.text_controls):
            text_control = container.content
            if not isinstance(text_control, ft.Text):
                continue

            is_current = index == self.current_line
            text_control.weight = (
                ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL
            )
            container.bgcolor = self.background_color if is_current else None

    def update_theme(self, text_color: str, background_color: str) -> None:
        """
        Aggiorna i colori delle righe in base al tema corrente.
        """
        self.text_color = text_color
        self.background_color = background_color

        for index, container in enumerate(self.text_controls):
            text_control = container.content
            if not isinstance(text_control, ft.Text):
                continue

            text_control.color = text_color
            container.bgcolor = background_color if index == self.current_line else None

    def resize(self, ui_size: float) -> None:
        """
        Aggiorna la dimensione del testo.
        """
        self.ui_size = ui_size

        for container in self.text_controls:
            text_control = container.content
            if isinstance(text_control, ft.Text):
                text_control.size = ui_size
