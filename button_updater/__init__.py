import asyncpraw.models


__version__ = '1.0.0'


# todo: add argument to make it case sensitive
# todo: write docstrings
async def find_button_widget(subreddit: asyncpraw.models.Subreddit, name: str) -> asyncpraw.models.ButtonWidget:
    widgets_dict = await subreddit.widgets.items()
    button_widgets = [w for w in widgets_dict.values() if isinstance(w, asyncpraw.models.ButtonWidget)]

    for widget in button_widgets:
        if widget.shortName.casefold() == name.casefold():
            return widget

    raise KeyError(f'Button widget named {name} not found in subreddit {subreddit.name}')


async def find_button(button_widget: asyncpraw.models.ButtonWidget, name: str) -> asyncpraw.models.Button:
    for button in button_widget:
        if button.text.casefold() == name.casefold():
            return button

    raise KeyError(f'Button named {name} not found in button widget {button_widget.shortName}')


async def update_button(
        subreddit: asyncpraw.models.Subreddit,
        button_widget_name: str, button_name: str,
        new_button_text: str, new_button_url: str
):
    button_widget = await find_button_widget(subreddit, button_widget_name)
    button = await find_button(button_widget, button_name)

    # todo: check if this works or if I have to do it with button_widget.mod.update()
    # it doesn't work, need to use a different method
    # raises asyncprawcore.exceptions.Forbidden http 403 if not mod
    # also if sub is private
    button.text = new_button_text
    button.url = new_button_url

