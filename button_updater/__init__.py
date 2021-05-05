import asyncpraw.models


__version__ = '1.0.0'


# todo: handle if search term not found
async def find_button_widget(subreddit: asyncpraw.models.Subreddit, name: str) -> asyncpraw.models.ButtonWidget:
    all_widgets = await subreddit.widgets()
    widgets_dict = all_widgets.items()
    button_widgets = [w for w in widgets_dict.values() if isinstance(w, asyncpraw.models.ButtonWidget)]

    for widget in button_widgets:
        if widget.shortName.casefold() == name.casefold():
            return widget


async def find_button(button_widget: asyncpraw.models.ButtonWidget, name: str) -> asyncpraw.models.Button:
    for button in button_widget:
        if button.text.casefold() == name.casefold():
            return button


def update_button(
        subreddit: asyncpraw.models.Subreddit,
        button_widget_name: str, button_name: str,
        new_button_text: str, new_button_url: str
):
    button_widget = await find_button_widget(subreddit, button_widget_name)
    button = await find_button(button_widget, button_name)

    # todo: check if this works or if I have to do it with button_widget.mod.update()
    button.text = new_button_text
    button.url = new_button_url

