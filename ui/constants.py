"""
Defines app-specific constants.
"""

from core.constants import *
from ui.view.colors.themes import ThemeLibrary

APP_NAME = "Abalone"
FPS = 60

BOARD_CELL_SIZE = 48
MARBLE_SIZE = BOARD_CELL_SIZE * 7 / 8
BOARD_WIDTH = BOARD_CELL_SIZE * BOARD_MAX_COLS
BOARD_HEIGHT = BOARD_CELL_SIZE * BOARD_MAX_COLS * 7 / 8

DEBUG = True
DEBUG_LOADS_ON_START = DEBUG
DEBUG_FILEPATH = "debug.json"

DEFAULT_THEME = ThemeLibrary.DEFAULT
