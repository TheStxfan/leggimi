import flet as ft

from leggimi.errors import UIInitializationError
from leggimi.models.app_state import AppState
from leggimi.ui.ui_components import (
    create_button,
    create_theme_switch_button,
    create_ui_size_slider,
)
from leggimi.ui.ui_theme import set_theme_mode


async def main(page: ft.Page):
    """
    Inizializza l'interfaccia grafica dell'applicazione LeggiMi.

    Args:
        page: Pagina Flet utilizzata per costruire e visualizzare
            l'interfaccia.

    Returns:
        None.

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
        ),
        expand=True,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    app_state = AppState(
        page=page,
        file_picker=file_picker,
        main_content=main_content,
    )

    select_pdf_button = create_button(
        "Seleziona un PDF",
        ft.Icons.UPLOAD_FILE,
        app_state.select_pdf,
        tooltip_text=("Seleziona un file PDF da convertire in audio"),
    )

    ui_size_row = create_ui_size_slider()
    theme_button = create_theme_switch_button()

    main_content.content.controls.append(  # type: ignore
        select_pdf_button,
    )

    page.add(
        ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    expand=True,
                    margin=ft.Margin.only(top=20),
                    controls=[
                        main_content,
                        ui_size_row,
                    ],
                ),
                ft.Container(
                    content=theme_button,
                    right=20,
                    bottom=20,
                ),
            ],
        ),
    )


ft.run(main)
