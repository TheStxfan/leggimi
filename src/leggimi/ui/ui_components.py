import flet as ft
from leggimi.ui.ui_config import UI_SIZE

button_scale = UI_SIZE ** (1 / 16) - 0.2
text_size = UI_SIZE
button_offset = ft.Offset((button_scale - 1) / 2, (button_scale - 1) / 2)


def create_button(
    text: str,
    icon,
    on_click,
    size: float = UI_SIZE,
) -> ft.Button:
    return ft.Button(
        content=ft.Text(text, size=size),
        icon=ft.Icon(icon, size=size),
        offset=button_offset,
        scale=button_scale,
        on_click=on_click,
        align=ft.Alignment.CENTER,
    )


def create_text(
    text: str,
    size: float = text_size,
) -> ft.Text:
    return ft.Text(
        text,
        size=size,
        align=ft.Alignment.CENTER,
    )
