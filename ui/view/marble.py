"""
Contains marble-specific view logic.
"""

from dataclasses import dataclass
from typing import Tuple

from core.color import Color
import ui.view.colors.palette as palette
from ui.view.colors.transform import darken_color, lighten_color


@dataclass
class Marble:
    """
    Represents the view for a single marble.
    """
    pos: Tuple[float]
    cell: Tuple[int]
    color: Color
    object_ids: list
    selected: bool = False
    focused: bool = False
    highlighted: bool = False


def render_marble(canvas, pos, color, size, selected=False, focused=False, highlighted=False):
    """
    Renders a marble using the given paramters.
    :param canvas: the Canvas to render to
    :param pos: a tuple[int, int] denoting where on the canvas to draw
    :param color: a str (hex color)
    :param size: an int denoting how large the marble should be drawn
    :param selected: a bool denoting whether or not to draw the marble as selected
    :param focused: a bool denoting whether or not to draw the marble as focused
    :param highlighted: a bool denoting whether or not to draw the marble as highlighted
    :return: a list[int] of Tk object ids
    """

    MARBLE_COLOR = darken_color(color) if selected else color

    marble_shape_ids = []
    x, y = pos
    s = size

    # marble body
    marble_shape_ids.append(canvas.create_oval(
        x - s / 2, y - s / 2,
        x + s / 2, y + s / 2,
        fill=MARBLE_COLOR,
        outline=darken_color(MARBLE_COLOR),
        width=2,
    ))

    # marble highlight outline
    if highlighted:
        RING_WIDTH = 2
        RING_SIZE = s / 2 + 2
        marble_shape_ids.append(canvas.create_oval(
            x - RING_SIZE, y - RING_SIZE,
            x + RING_SIZE, y + RING_SIZE,
            fill="",
            outline=palette.COLOR_YELLOW,
            width=RING_WIDTH,
        ))

    # marble selection outline
    if focused:
        RING_WIDTH = 3
        RING_MARGIN = 2
        RING_SIZE = s / 2 + 2
        marble_shape_ids.append(canvas.create_oval(
            x - RING_SIZE - RING_WIDTH, y - RING_SIZE - RING_WIDTH,
            x + RING_SIZE + RING_MARGIN, y + RING_SIZE + RING_MARGIN,
            fill="",
            outline=lighten_color(color),
            width=RING_WIDTH,
        ))

    # marble highlights
    HIGHLIGHT_SIZE = s * 3 / 4
    HIGHLIGHT_X = x - HIGHLIGHT_SIZE / 2
    HIGHLIGHT_Y = y - HIGHLIGHT_SIZE / 2
    marble_shape_ids.append(canvas.create_oval(
        HIGHLIGHT_X, HIGHLIGHT_Y,
        HIGHLIGHT_X + HIGHLIGHT_SIZE, HIGHLIGHT_Y + HIGHLIGHT_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    ))
    HIGHLIGHT_NEGATIVE_SIZE = HIGHLIGHT_SIZE + HIGHLIGHT_SIZE / 32
    marble_shape_ids.append(canvas.create_oval(
        x - s / 2 + s / 16, y - s / 2 + s / 16,
        x - s / 2 + s / 16 + HIGHLIGHT_NEGATIVE_SIZE, y - s / 2 + s / 16 + HIGHLIGHT_NEGATIVE_SIZE,
        fill=MARBLE_COLOR,
        outline="",
    ))
    marble_shape_ids.append(canvas.create_oval(
        x - s / 2 + s / 4, y - s / 32,
        x + s / 2 - s / 4, y - s / 32 + s / 3,
        fill=darken_color(MARBLE_COLOR),
        outline="",
    ))
    HIGHLIGHT_BALANCE_SIZE = HIGHLIGHT_SIZE / 3
    HIGHLIGHT_BALANCE_X = x - HIGHLIGHT_SIZE / 8
    HIGHLIGHT_BALANCE_Y = y - HIGHLIGHT_SIZE / 6
    marble_shape_ids.append(canvas.create_oval(
        HIGHLIGHT_BALANCE_X, HIGHLIGHT_BALANCE_Y,
        HIGHLIGHT_BALANCE_X + HIGHLIGHT_BALANCE_SIZE, HIGHLIGHT_BALANCE_Y + HIGHLIGHT_BALANCE_SIZE,
        fill=MARBLE_COLOR,
        outline="",
    ))

    # marble shine
    SHINE_X = x - s / 4
    SHINE_Y = y - s / 3
    SHINE_SIZE = s / 4
    marble_shape_ids.append(canvas.create_oval(
        SHINE_X, SHINE_Y,
        SHINE_X + SHINE_SIZE, SHINE_Y + SHINE_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    ))

    # marble shine core
    SHINE_CORE_OFFSET = s / 24
    SHINE_CORE_X = SHINE_X + SHINE_CORE_OFFSET * 3 / 4
    SHINE_CORE_Y = SHINE_Y + SHINE_CORE_OFFSET * 3 / 4
    SHINE_CORE_SIZE = SHINE_SIZE - SHINE_CORE_OFFSET * 2
    marble_shape_ids.append(canvas.create_oval(
        SHINE_CORE_X, SHINE_CORE_Y,
        SHINE_CORE_X + SHINE_CORE_SIZE, SHINE_CORE_Y + SHINE_CORE_SIZE,
        fill=palette.COLOR_WHITE,
        outline="",
    ))

    # marble secondary shine
    SHINE_SECONDARY_X = x - s / 3
    SHINE_SECONDARY_Y = y - s / 8
    SHINE_SECONDARY_SIZE = s / 10
    marble_shape_ids.append(canvas.create_oval(
        SHINE_SECONDARY_X, SHINE_SECONDARY_Y,
        SHINE_SECONDARY_X + SHINE_SECONDARY_SIZE, SHINE_SECONDARY_Y + SHINE_SECONDARY_SIZE,
        fill=lighten_color(MARBLE_COLOR),
        outline="",
    ))

    return marble_shape_ids
