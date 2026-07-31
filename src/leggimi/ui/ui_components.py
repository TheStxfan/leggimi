import flet as ft

from leggimi.models import Chapter
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

        if isinstance(control.tooltip, ft.Tooltip):
            control.tooltip.text_style = ft.TextStyle(
                size=new_size * 0.7,
                color="amber",
            )

    elif isinstance(control, ft.ListTile):
        if isinstance(control.title, ft.Control):
            resize_ui(
                control.title,
                new_size,
                exclude,
            )

    elif isinstance(control, ft.Dropdown):
        page_width = control.page.width or 1500 if control.page else 1500
        page_height = control.page.height or 750 if control.page else 750

        dropdown_scale = new_size ** (1 / 4)

        control.width = page_width * 0.2 * dropdown_scale
        control.height = new_size * 2.2

        control.text_style = ft.TextStyle(
            size=new_size,
            color="amber",
        )

        control.label_style = ft.TextStyle(
            color="amber",
            size=new_size * 0.7,
        )

        if control.leading_icon:
            control.leading_icon.size = new_size * 1.2  # type: ignore

        if control.trailing_icon:
            control.trailing_icon.size = new_size  # type: ignore

        if control.selected_trailing_icon:
            control.selected_trailing_icon.size = new_size  # type: ignore

        control.menu_style = ft.MenuStyle(
            fixed_size=ft.Size(
                width=((control.page.width or 1500) * 0.2) * (new_size ** (1 / 4)),
                height=((control.page.height or 750) * 0.15) * (new_size ** (1 / 4)),
            ),
        )

        for option in control.options:
            option.style = ft.ButtonStyle(
                color="amber",
                text_style=ft.TextStyle(
                    size=new_size,
                ),
            )

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
    min_size: float = 35,
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
        thumb_color="amber",
        active_color="amber",
        value=UI_SIZE,
        tooltip=(
            ft.Tooltip(
                message="Modifica la scala interfaccia",
                text_style=ft.TextStyle(
                    size=current_ui_size * 0.8,
                    color="amber",
                ),
                bgcolor=ft.Colors.GREY_900,
            )
        ),
        label=f"{initial_percentage:.0f}%",
        width=300,
        on_change=resize_ui_handler,
    )

    row = ft.Row(
        margin=ft.Margin.only(top=15),
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
    tooltip_text: str | None = None,
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

    button_scale = current_ui_size ** (1 / 16) - 0.2
    button_offset = ft.Offset(
        0,
        (button_scale - 1) / 2,
    )

    return ft.Button(
        content=ft.Text(text, size=size),
        icon=ft.Icon(icon, size=size),  # type: ignore
        offset=button_offset,
        scale=button_scale,
        color="amber",
        on_click=on_click,
        tooltip=(
            ft.Tooltip(
                message=tooltip_text,
                text_style=ft.TextStyle(
                    size=current_ui_size * 0.7,
                    color="amber",
                ),
                bgcolor=ft.Colors.GREY_900,
            )
            if tooltip_text is not None
            else None
        ),
        align=ft.Alignment.CENTER,
        style=ft.ButtonStyle(
            side={
                ft.ControlState.FOCUSED: ft.BorderSide(
                    width=3,
                    color=ft.Colors.AMBER,
                ),
            },
        ),
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
        color="amber",
        size=(current_ui_size if size is None else size),
        align=ft.Alignment.CENTER,
    )


def create_chapters_dropdown(
    chapters: list[Chapter],
    # tooltip_text: str | None = None,
    page: ft.Page,
    size: float | None = None,
) -> ft.Container:
    """
    Crea un menu Dropdown Flet con testo e icona.

    Args:
        chapters: Lista di capitoli contenenti titolo e testo.
        size: Dimensione del testo e dell'icona.

    Returns:
        Pulsante Flet configurato.
    """

    if size is None:
        size = current_ui_size

    dropdown_scale = current_ui_size ** (1 / 4)
    dropdown_width = ((page.width or 1500) * 0.2) * dropdown_scale
    dropdown_menu_height = ((page.height or 750) * 0.15) * dropdown_scale

    return ft.Container(
        margin=ft.Margin.only(
            top=current_ui_size * 0.3,
        ),
        content=ft.Dropdown(
            color="amber",
            autofocus=True,
            border=ft.InputBorder.UNDERLINE,
            border_color="amber",
            border_width=2,
            width=dropdown_width,
            height=current_ui_size * 2.2,
            align=ft.Alignment.CENTER,
            label="Seleziona un capitolo",
            text_style=ft.TextStyle(
                size=current_ui_size,
                color="amber",
            ),
            menu_style=ft.MenuStyle(
                fixed_size=ft.Size(
                    width=dropdown_width,
                    height=dropdown_menu_height,
                ),
            ),
            options=[
                ft.DropdownOption(
                    key=str(idx),
                    text=chapter.title,
                    style=ft.ButtonStyle(
                        color="amber",
                        text_style=ft.TextStyle(
                            size=current_ui_size,
                        ),
                    ),
                )
                for idx, chapter in enumerate(chapters)
            ],
            label_style=ft.TextStyle(
                color="amber",
                size=current_ui_size * 0.7,
            ),
            value="0",
            leading_icon=ft.Icon(
                ft.Icons.SEARCH,
                color="amber",
                size=current_ui_size * 1.2,
            ),
            trailing_icon=ft.Icon(
                ft.Icons.ARROW_DROP_DOWN,
                color="amber",
                size=current_ui_size,
            ),
            selected_trailing_icon=ft.Icon(
                ft.Icons.ARROW_DROP_UP,
                color="amber",
                size=current_ui_size,
            ),
        ),
    )
