"""
Defines the model for the application.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import time

from dataclasses import dataclass, field
from lib.interval_timer import IntervalTimer
from agent.state_generator import StateGenerator
from core.board import Board
from core.color import Color
from core.constants import WIN_SCORE
from core.game import Game
from core.move import Move
from core.hex import HexDirection
from core.player_type import PlayerType
from core.selection import Selection
from ui.model.game_history import GameHistory, GameHistoryItem
from ui.model.config import Config
from ui.constants import FPS

if TYPE_CHECKING:
    from core.hex import Hex
    from core.board_layout import BoardLayout


@dataclass  # TODO(?): un-dataclass for field privacy
class Model:
    """
    The model for the application.
    Contains view-agnostic application state.
    """

    paused: bool = False
    selection: Selection = None
    timer: IntervalTimer = None
    timeout_move: Move = None

    move_start_time = None
    move_paused_start_time = None
    move_paused_duration = 0

    history: GameHistory = field(default_factory=GameHistory)
    game: Game = None
    config: Config = field(default_factory=Config.from_default)

    def __post_init__(self):
        self.game = Game(starting_layout=self.config.layout)

    @property
    def game_board(self):
        """
        Gets the game board.
        :return: a Board
        """
        return self.game.board

    @property
    def game_turn(self):
        """
        Gets the color indicating whose turn it is.
        :return: a Color
        """
        return self.game.turn

    @property
    def game_config(self):
        """
        Gets the config of the game.
        :return: a Config
        """
        return self.config

    def get_turn_count(self, player: Color) -> int:
        """
        Gets the turn count for a player.
        :return: the turn count
        """
        return len(self.history.get_player_history(player))

    def select_cell(self, cell: Hex):
        """
        Selects the given cell.
        :param: the Hex to select
        :return: the Move to perform if applicable, else None
        """

        selection = self.selection
        selection_head = selection and selection.get_head()

        # disallow selection if is paused
        if self.paused:
            return None

        # disallow selection if is computer
        if self.config.get_player_type(self.game_turn) is PlayerType.COMPUTER:
            self.selection = None
            return None

        # select marbles corresponding to the current turn
        if not selection:
            if cell in self.game_board and self.game_board[cell] == self.game_turn:
                self.selection = Selection(start=cell, end=cell)
            return None

        # deselect if out of bounds
        if cell not in self.game_board:
            self.selection = None
            return None

        # select new end cell if possible
        if self.game_board[cell] == self.game_turn:
            selection.start = selection.end or selection.start
            selection.end = cell
            if selection.is_valid_selection(self.game_board):
                self.selection = None
            return None

        # perform move if cell is adjacent to last clicked cell
        if selection_head.adjacent(cell):
            normal = cell.subtract(selection_head)
            direction = HexDirection.resolve(normal)
            move = Move(selection, direction)
            if self.game_board.is_valid_move(move, self.game_turn):
                return move

        self.selection = None
        return None  # consistency

    def undo(self) -> GameHistoryItem:
        layout = self.game.board.layout

        new_board = Board.create_from_data(layout)
        new_history = GameHistory()

        for item in self.history[:-2]:
            new_board.apply_move(item.move)
            new_history.append(GameHistoryItem(item.time_start, item.time_end, item.paused_duration, item.move))

        if len(self.history) > 1:
            next_item = self.history[-2]
        else:
            next_item = None

        self.game.set_board(new_board)
        self.history = new_history

        self.game.set_turn(self.history.infer_player_turn())

        return next_item

    def load_game_state(self, starting_layout: BoardLayout, game_history: GameHistory):
        """
        Loads game state from a given layout and history.
        :param starting_layout: a BoardLayout
        :param game_history: a GameHistory
        """
        board = Board.create_from_data(starting_layout.value)
        for item in game_history:
            board.apply_move(item.move)

        self.game.set_board(board)
        self.game.set_turn(game_history.infer_player_turn())
        self.config.layout = starting_layout
        self.history = game_history

    def reset(self):
        """
        Resets the model to the default state.
        """
        self.stop_timer()

        self.paused = False
        self.move_start_time = None
        self.move_paused_start_time = None
        self.move_paused_duration = 0
        self.timeout_move = None
        self.selection = None

        self.history = GameHistory()
        self.game = Game(self.config.layout)

    def toggle_pause(self):
        self.paused = not self.paused

        if self.paused:
            self.move_paused_start_time = time.time()
        else:
            self.move_paused_duration += time.time() - self.move_paused_start_time
            self.move_paused_start_time = None

        if self.timer:
            self.timer.toggle_pause()

    def apply_config(self, config: Config):
        """
        Applies the given config.
        :param config: the new Config to use
        :return: None
        """
        self.config = config

    def apply_move(self, move: Move):
        """
        Applies the given move to the game board.
        :param move: the move to apply
        """
        self.selection = None

        self.stop_timer()
        self.game.apply_move(move)
        self.history.append(GameHistoryItem(self.move_start_time, time.time(), self.move_paused_duration, move))

    def next_turn(self, on_timer: callable, on_timeout: callable, on_game_end: callable):
        """
        Stores starting time and starts timer for the move.
        :param on_timer: the callable for each timer tick
        :param on_timeout: the callable for when timer is complete
        :param on_game_end: the callable for when move limit is reached
        :return: If the game successfully moved to the next turn
        """
        if self.get_turn_count(self.game_turn) >= self.config.move_limit \
           or self.game.board.get_score(Color.next(self.game_turn)) >= WIN_SCORE:
            on_game_end()
            return False

        self.move_start_time = time.time()
        self.move_paused_duration = 0

        self._timer_launch(on_timer, on_timeout)
        return True

    def stop_timer(self):
        if self.timer:
            self.timer.stop()

    def _timer_launch(self, on_timer: callable, on_timeout: callable):
        """
        Launches the turn timer.
        :param on_timer: A function that is called every timer update.
        :param on_timeout: A function that is called when the timer runs out of time.
        :return:
        """
        self.stop_timer()

        self.timeout_move = None

        time_limit = self.game_config.get_player_time_limit(self.game_turn)

        self.timer = IntervalTimer(time_limit, 1 / FPS)
        self.timer.set_on_interval(lambda progress: self._timer_on_interval(on_timer, progress))
        self.timer.set_on_complete(lambda: self._timer_on_complete(on_timeout))
        self.timer.start()

    def _timer_on_interval(self, on_timer: callable, progress: float):
        """
        Converts timer progress into time remaining and calls on_timer().
        """
        time_remaining = self.timer.total_time * progress
        on_timer(time_remaining)

    def _timer_on_complete(self, on_timeout: callable):
        """
        Calls on_timeout().
        Sets timeout move to a random generated one if unset.
        """
        if not self.timeout_move:
            self.timeout_move = StateGenerator.generate_random_move(self.game_board, self.game_turn)
        on_timeout()
