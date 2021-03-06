"""
Defines pondering agent implementation logic.
"""

from math import inf
from copy import deepcopy
from threading import Thread

from agent.ponderer import PonderingAgent
from agent.brandon.search import Search
from agent.state_generator import StateGenerator
from agent.zobrist import Zobrist
from core.board import Board
from core.color import Color
from core.move import Move
from ui.model.heuristic_type import HeuristicType
from ui.debug import Debug, DebugType
from ui.constants import DEBUG


def search_worker(search, board, color, on_find, on_complete):
    """
    Manages the default search task.
    :param search: a Search instance
    :param board: a Board
    :param color: a Color
    :param on_find: a Callable[Move]
    :param on_complete: a Callable
    """
    search.start(board, color, on_find=on_find)
    on_complete()

def ponder_worker(search, refutation_table, board, color, on_find, on_complete):
    """
    Manages the pondering search task.
    Caches a defined number of refutations for each opponent move.
    :param search: a Search instance
    :param refutation_table: a dict[Board, Move]
    :param board: a Board
    :param color: a Color
    :param on_find: a Callable[Move, Move] mapping predictions to refutations
    :param on_complete: a Callable
    """

    # The number of predictions i.e. refutations to cache.
    # More predictions result in a higher hit rate but will keep the thread busy.
    # Probably best as `inf` in competitive settings to maximize transposition table hits.
    NUM_PREDICTIONS = inf

    temp_board = deepcopy(board)
    def find_move_score(move):
        temp_board.apply_move(move)
        move_score = search.heuristic.call(temp_board, color)
        temp_board.copy_state(board)
        return move_score

    # find x amount of most likely moves (ordered by heuristic)
    opponent_moves = StateGenerator.enumerate_board(board, color)
    opponent_moves.sort(key=find_move_score, reverse=True)

    if NUM_PREDICTIONS != inf:
        opponent_moves = opponent_moves[:NUM_PREDICTIONS]

    best_move = None
    def set_best_move(move):
        nonlocal best_move
        best_move = move

    # determine refutations for each opponent move
    for opponent_move in opponent_moves:
        temp_board.apply_move(opponent_move)

        best_move = None
        exhausted = search.start(temp_board, Color.next(color), on_find=set_best_move)
        if exhausted and best_move:
            Debug.log(f"set refutation for {opponent_move} -> {best_move}", DebugType.Agent)
            opponent_hash = Zobrist.create_board_hash(temp_board)
            refutation_table[opponent_hash] = best_move
            if on_find:
                on_find(opponent_move, best_move)

        if search.stopped:
            break

        temp_board.copy_state(board)

    if on_complete:
        on_complete()


class BrandonPonderer(PonderingAgent):
    """
    Demonstrates usage of the pondering agent interface.
    """

    def __init__(self):
        super().__init__()
        self._search = Search()
        self._search_mode = None
        self._thread = None

    @property
    def is_searching(self):
        return self._thread is not None and self._thread.is_alive()

    def _create_normal_search_thread(self, board: Board, player: Color,
                                     on_find: callable, on_complete: callable):
        return Thread(target=search_worker, args=(
            self._search,
            board,
            player,
            on_find,
            on_complete
        ))

    def _create_ponder_search_thread(self, board: Board, player: Color,
                                     on_find: callable, on_complete: callable):
        return Thread(target=ponder_worker, args=(
            self._search,
            self._refutation_table,
            board,
            player,
            on_find,
            on_complete
        ))

    def _start_search(self, thread):
        thread.daemon = True
        thread.start()
        self._thread = thread

    def start(self, board: Board, player: Color, on_find: callable, on_complete: callable):
        thread = self._create_normal_search_thread(board, player, on_find, on_complete)
        self._search_mode = self.SearchMode.NORMAL_SEARCH
        self._start_search(thread)

    def ponder(self, board: Board, player: Color,
               on_find: callable = None, on_complete: callable = None):
        self.clear_refutation_table()
        thread = self._create_ponder_search_thread(board, player, on_find, on_complete)
        self._search_mode = self.SearchMode.PONDER_SEARCH
        self._start_search(thread)

    def stop(self):
        self._search.stop()
        self._search_mode = None

    def toggle_paused(self):
        self._search.toggle_paused()

    def apply_move(self, move: Move):
        self.stop()

    def set_heuristic_type(self, heuristic_type: HeuristicType):
        self._search.heuristic = heuristic_type
