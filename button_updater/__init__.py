import typing
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
    for button in button_widget.buttons:
        if button.text.casefold() == name.casefold():
            return button

    raise KeyError(f'Button named {name} not found in button widget {button_widget.shortName}')


def button_widget_to_json(button_widget: asyncpraw.models.ButtonWidget) -> typing.Dict[str, dict]:
    buttons_json = {}

    for button in button_widget.buttons:
        # attributes every button has
        button_dict = {
            'kind': button.kind,
            'color': button.color,
            'fillColor': button.fillColor,
            'text': button.text,
            'textColour': button.textColour,
            'url': button.url,
        }
        # attributes it may have
        if hasattr(button, 'hoverState'):
            button_dict['hoverState'] = button.hoverState
        # attributes depending on type
        if button.kind == 'image':
            button_dict['height'] = button.height
            button_dict['width'] = button.width
            button_dict['linkUrl'] = button.linkUrl

        buttons_json[button.text] = button_dict

    return buttons_json


async def update_button(
        subreddit: asyncpraw.models.Subreddit,
        button_widget_name: str, button_name: str,
        new_button_text: str, new_button_url: str
):
    button_widget = await find_button_widget(subreddit, button_widget_name)
    button = await find_button(button_widget, button_name)

    # raises asyncprawcore.exceptions.Forbidden http 403 if not mod
    # also if sub is private
    buttons_json = button_widget_to_json(button_widget)
    buttons_json[button.text]['text'] = new_button_text
    buttons_json[button.text]['url'] = new_button_url

    await button_widget.mod.update(buttons=[buttons_json.values()])
