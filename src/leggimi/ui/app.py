import flet as ft

from leggimi.errors import LeggiMiError, UIInitializationError
from leggimi.models.app_state import AppState
from leggimi.ui import ui_theme
from leggimi.ui.ui_components import (
    create_global_settings_row,
    create_button,
    create_theme_switch_button,
    create_ui_size_slider,
)
from leggimi.ui.ui_config import UI_SIZE
from leggimi.ui.ui_theme import set_theme_mode


async def main(page: ft.Page):
    """
    Inizializza l'interfaccia grafica dell'applicazione.

    Args:
        page: Pagina Flet utilizzata per costruire e visualizzare
            l'interfaccia.

    Raises:
        UIInitializationError: Se si verifica un errore durante
            l'inizializzazione dell'interfaccia grafica.
    """

    try:
        page.title = "LeggiMi"

        set_theme_mode(page)

        file_picker = ft.FilePicker()
        page.services.append(file_picker)

    except Exception as exc:
        raise UIInitializationError(
            "Errore durante l'inizializzazione dell'interfaccia.",
        ) from exc

    main_content = ft.Container(
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=ft.Padding.only(
            top=UI_SIZE * 0.4,
            bottom=80,
        ),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    ui_size_row = create_ui_size_slider()

    bottom_bar = ft.Container(
        content=ui_size_row,
        left=0,
        right=0,
        bottom=0,
        padding=ft.Padding.only(bottom=15),
    )

    theme_button = create_theme_switch_button()

    app_stack = ft.Stack(
        expand=True,
        controls=[
            main_content,
            bottom_bar,
            ft.Container(
                content=theme_button,
                right=15,
                bottom=15,
            ),
        ],
    )

    app_state = AppState(
        page=page,
        file_picker=file_picker,
        main_content=main_content,
        app_stack=app_stack,
        bottom_bar=bottom_bar,
        ui_size_row=ui_size_row,
    )

    settings_row, mode_dropdown, level_dropdown = create_global_settings_row(
        on_select=lambda e: app_state._update_audio_button(),
    )

    app_state.mode_dropdown = mode_dropdown
    app_state.level_dropdown = level_dropdown

    select_pdf_button = create_button(
        "Seleziona un PDF",
        ft.Icons.FILE_UPLOAD,
        app_state.select_pdf,
        tooltip_text="Seleziona un file PDF da convertire in audio",
    )

    main_content.content.controls.extend(  # type: ignore
        [
            settings_row,
            select_pdf_button,
        ]
    )

    page.add(app_stack)
    page.run_task(
        app_state._show_error,
        LeggiMiError("Errore di test"),
    )

    async def on_window_event(e: ft.WindowEvent) -> None:
        if e.type == ft.WindowEventType.CLOSE:

            if app_state.audio_player is not None:
                app_state.audio_player.cleanup()

            page.window.prevent_close = False
            await page.window.close()

    page.window.prevent_close = True
    page.window.on_event = on_window_event


ft.run(main)
