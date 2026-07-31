from dataclasses import dataclass

import flet as ft

from leggimi.ui.ui_config import THEME


@dataclass
class ThemeConfig:
    primary_text_color: str
    tooltip_bgcolor: str


theme_config = ThemeConfig(
    primary_text_color="",
    tooltip_bgcolor="",
)


def set_theme_mode(
    page: ft.Page,
    theme: str = THEME,
) -> ThemeConfig:

    if theme == "light":
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = "#FDFBF7"

        theme_config.primary_text_color = "#2D2D2D"
        theme_config.tooltip_bgcolor = "#E8E4D9"

    elif theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#121212"

        theme_config.primary_text_color = "amber"
        theme_config.tooltip_bgcolor = "#1E1E1E"

    page.theme = ft.Theme(
        font_family="Roboto",
    )

    page.fonts = {
        "Roboto": "fonts/Roboto-Regular.ttf",
    }

    return theme_config
