import typing
import asyncpraw.models


__version__ = '1.0.0'


async def find_button_widget(
        subreddit: asyncpraw.models.Subreddit, name: str, case_sensitive: bool = False
) -> asyncpraw.models.ButtonWidget:
    """Return the first button widget in the given subreddit that has the given name.

    Raises KeyError if no button widget in the subreddit has that name.
    """
    widgets_dict = await subreddit.widgets.items()
    button_widgets = [w for w in widgets_dict.values() if isinstance(w, asyncpraw.models.ButtonWidget)]

    for widget in button_widgets:
        widget_name = widget.shortName
        search_name = name
        if not case_sensitive:
            widget_name = widget_name.casefold()
            search_name = search_name.casefold()

        if widget_name == search_name:
            return widget

    raise KeyError(f'Button widget named {name} not found in subreddit {subreddit.name}')


async def find_button(
        button_widget: asyncpraw.models.ButtonWidget, name: str, case_sensitive: bool = False
) -> asyncpraw.models.Button:
    """Return the first button in the given button widget that has the given name (text).

    Raises KeyError if no button in the button widget has that name.
    """
    for button in button_widget.buttons:
        button_name = button.text
        search_name = name
        if not case_sensitive:
            button_name = button_name.casefold()
            search_name = search_name.casefold()

        if button_name == search_name:
            return button

    raise KeyError(f'Button named {name} not found in button widget {button_widget.shortName}')


def button_widget_to_json(button_widget: asyncpraw.models.ButtonWidget) -> typing.Dict[str, dict]:
    """Given a button widget, convert it to a dict that could be given to the reddit API to duplicate the widget.

    Note: returns a dict of button text, button attribute pairs. To get it in the exact format that the reddit API
    takes, use button_widget_to_json(button_widget).values()
    """
    # todo: what if there are buttons with the same text
    buttons_json = {}

    for button in button_widget.buttons:
        # attributes every button has
        # todo: convert this to code like the lot below, and make that a function?
        button_dict = {
            'kind': button.kind,
            'color': button.color,
            'text': button.text,
            'url': button.url,
        }
        # attributes it may have
        optional_attrs = ['hoverState']
        for attr in optional_attrs:
            if hasattr(button, attr):
                button_dict[attr] = getattr(button, attr)
        # attributes it may have with defaults
        defaulting_attrs = {'fillColor': '#000000', 'textColor': '#FFFFFF'}
        for attr in defaulting_attrs:
            if hasattr(button, attr):
                button_dict[attr] = getattr(button, attr)
            else:
                button_dict[attr] = defaulting_attrs[attr]
        # attributes depending on type
        if button.kind == 'image':
            image_attrs = ['height', 'width', 'linkUrl']
            for attr in image_attrs:
                if hasattr(button, attr):
                    button_dict[attr] = getattr(button, attr)

        buttons_json[button.text] = button_dict

    return buttons_json


async def update_button(
        subreddit: asyncpraw.models.Subreddit,
        button_widget_name: str, button_name: str,
        new_button_text: str, new_button_url: str
):
    """Search a subreddit for a button and update it.

    Args:
        subreddit -- the subreddit object in which to search
        button_widget_name -- name of the button widget to search for
        button_name -- name (text) of the button within the button widget to search for
        new_button_text -- if found, the button's text will be set to this
        new_button_url -- like new_button_text

    Raises:
        prawcore.errors.Forbidden with http code 402 if you do not have access to the subreddit (private subreddits),
            or if you are not a moderator of the subreddit and cannot update the button
        KeyError if there is no match for one of the given search terms
    """
    button_widget = await find_button_widget(subreddit, button_widget_name)
    button = await find_button(button_widget, button_name)

    # raises asyncprawcore.exceptions.Forbidden http 403 if not mod
    # also if sub is private
    buttons_json = button_widget_to_json(button_widget)
    buttons_json[button.text]['text'] = new_button_text
    buttons_json[button.text]['url'] = new_button_url

    print(list(buttons_json.values()))
    await button_widget.mod.update(buttons=[list(buttons_json.values())])
