import flet as ft

from leggimi.ui.ui_config import UI_SIZE

current_ui_size = UI_SIZE


def resize_ui(
    control: ft.Control,
    new_size: float,
    exclude: ft.Control | None = None,
) -> None:
    """
    Ridimensiona ricorsivamente i componenti UI.

    Args:
        control: Controllo Flet da ridimensionare.
        new_size: Nuova dimensione base dell'interfaccia.
        exclude: Controllo da escludere dal ridimensionamento.

    Returns:
        None.
    """

    if control is exclude:
        return

    button_scale = new_size ** (1 / 16) - 0.2
    button_offset = ft.Offset(
        (button_scale - 1) / 2,
        (button_scale - 1) / 2,
    )

    if isinstance(control, ft.Text):
        control.size = new_size

    elif isinstance(control, ft.Button):
        control.scale = button_scale
        control.offset = button_offset

        if isinstance(control.content, ft.Text):
            control.content.size = new_size

        if control.icon is not None:
            control.icon.size = new_size  # type: ignore

    if hasattr(control, "controls"):
        for child in control.controls:  # type: ignore
            resize_ui(child, new_size, exclude)

    if hasattr(control, "content") and isinstance(
        control.content,  # type: ignore
        ft.Control,
    ):
        resize_ui(
            control.content,  # type: ignore
            new_size,
            exclude,
        )


def create_ui_size_slider(
    min_size: float = 26,
    max_size: float = 80,
) -> tuple[ft.Row, ft.Text]:
    """
    Crea lo slider per modificare la dimensione dell'interfaccia.

    Args:
        min_size: Dimensione minima dell'interfaccia.
        max_size: Dimensione massima dell'interfaccia.

    Returns:
        Una tupla contenente il Row dello slider e il testo
        utilizzato per visualizzare l'etichetta "UI Size".
    """

    ui_size_text = create_text("UI Size")

    def resize_ui_handler(e):
        """
        Aggiorna la dimensione dell'interfaccia in base al valore
        selezionato nello slider.

        Args:
            e: Evento generato dalla modifica del valore dello slider.

        Returns:
            None.
        """

        global current_ui_size

        new_size = e.control.value
        current_ui_size = new_size

        percentage = (new_size - min_size) / (max_size - min_size) * 100

        e.control.label = f"{percentage:.0f}%"

        resize_ui(
            e.page,
            new_size,
            exclude=ui_size_text,
        )

        e.page.update()

    initial_percentage = (UI_SIZE - min_size) / (max_size - min_size) * 100

    ui_size_slider = ft.Slider(
        min=min_size,
        max=max_size,
        divisions=10,
        value=UI_SIZE,
        label=f"{initial_percentage:.0f}%",
        width=300,
        on_change=resize_ui_handler,
    )

    row = ft.Row(
        margin=ft.Margin.only(top=30),
        controls=[
            ui_size_text,
            ui_size_slider,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return row, ui_size_text


def create_button(
    text: str,
    icon,
    on_click,
    size: float | None = None,
) -> ft.Button:
    """
    Crea un pulsante Flet con testo e icona.

    Args:
        text: Testo visualizzato nel pulsante.
        icon: Icona visualizzata nel pulsante.
        on_click: Funzione eseguita al clic sul pulsante.
        size: Dimensione del testo e dell'icona.

    Returns:
        Pulsante Flet configurato.
    """

    if size is None:
        size = current_ui_size

    button_scale = size ** (1 / 16) - 0.2
    button_offset = ft.Offset(
        (button_scale - 1) / 2,
        (button_scale - 1) / 2,
    )

    return ft.Button(
        content=ft.Text(
            text,
            size=size,
        ),
        icon=ft.Icon(
            icon,
            size=size,
        ),
        offset=button_offset,
        scale=button_scale,
        on_click=on_click,
        align=ft.Alignment.CENTER,
    )


def create_text(
    text: str,
    size: float | None = None,
) -> ft.Text:
    """
    Crea un controllo di testo Flet.

    Args:
        text: Testo da visualizzare.
        size: Dimensione del testo. Se non specificata, viene utilizzata
            la dimensione corrente dell'interfaccia.

    Returns:
        Controllo di testo Flet configurato.
    """

    return ft.Text(
        text,
        size=(current_ui_size if size is None else size),
        align=ft.Alignment.CENTER,
    )
