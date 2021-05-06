"""Provides an asyncpraw function to search for a single Reddit button within a button widget and update it."""

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


def copyattrs(button: asyncpraw.models.Button, button_dict: dict, attrs: typing.Union[list, dict]) -> dict:
    """Copy attributes from the button to the dict if they exist.

    Args:
        button -- button to copy attrs from
        button_dict -- dict to copy attrs to
        attrs -- list of attr names to copy, or a dict of attr names to copy with default values
    Returns:
        button_dict with any applicable attrs added
    """
    for attr in attrs:
        if hasattr(button, attr):
            button_dict[attr] = getattr(button, attr)
        elif isinstance(attrs, dict):
            button_dict[attr] = attrs[attr]

    return button_dict


def button_widget_to_json(button_widget: asyncpraw.models.ButtonWidget) -> typing.List[dict]:
    """Given a button widget, convert it to a dict that could be given to the reddit API to duplicate the widget."""
    buttons_json = []

    for button in button_widget.buttons:
        # attributes every button has
        button_dict = {
            'kind': button.kind,
            'color': button.color,
            'text': button.text,
            'url': button.url,
        }
        # attributes it may have
        optional_attrs = ['hoverState']
        button_dict = copyattrs(button, button_dict, optional_attrs)
        # attributes it may have with defaults
        defaulting_attrs = {'fillColor': '#000000', 'textColor': '#FFFFFF'}
        button_dict = copyattrs(button, button_dict, defaulting_attrs)
        # attributes depending on type
        if button.kind == 'image':
            image_attrs = ['height', 'width', 'linkUrl']
            button_dict = copyattrs(button, button_dict, image_attrs)

        buttons_json.append(button_dict)

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
    # search to check if it exists
    button_widget = await find_button_widget(subreddit, button_widget_name)
    button = await find_button(button_widget, button_name)

    # get json to send to reddit api, then modify it
    buttons_json = button_widget_to_json(button_widget)
    for button_json in buttons_json:
        if button_json['text'] == button.text:
            button_json['text'] = new_button_text
            button_json['url'] = new_button_url
            break

    # send the api request to update the button
    await button_widget.mod.update(buttons=buttons_json)
