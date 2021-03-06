from abc import abstractmethod
from enum import Enum, auto
from core.board import Board
from core.color import Color
from agent.base import BaseAgent
from agent.zobrist import Zobrist
from ui.debug import Debug, DebugType


class PonderingAgent(BaseAgent):
    """
    An abstract base class for agents with pondering capabilities.
    Exposes an interface around a refutation table for mapping boards to refutation moves.
    """

    class SearchMode(Enum):
        """
        Enumerates possible search modes.
        """
        NORMAL_SEARCH = auto()
        PONDER_SEARCH = auto()

    def __init__(self):
        super().__init__()
        self._refutation_table = {}

    def get_refutation_move(self, board):
        """
        Gets the refutation move for the given board.
        :param board: a Board
        :return: a Move if refutation move is cached else None
        """
        board_hash = Zobrist.create_board_hash(board)

        if board_hash in self._refutation_table:
            Debug.log(f"refutation table hit {board_hash} -> {self._refutation_table[board_hash]}",
                DebugType.Agent)
        else:
            Debug.log(f"refutation table miss {board_hash} -> None",
                DebugType.Agent)

        return (self._refutation_table[board_hash]
            if board_hash in self._refutation_table
            else None)

    def set_refutation_move(self, board, refutation_move):
        """
        Sets the refutation move for the given board.
        :param board: a Board
        :param refutation_move: a Move
        """
        board_hash = Zobrist.create_board_hash(board)
        self._refutation_table[board_hash] = refutation_move

    def clear_refutation_table(self):
        """
        Clears the refutation table.
        """
        self._refutation_table.clear()

    @abstractmethod
    def ponder(self, board: Board, player: Color,
              on_find: callable, on_complete: callable = None):
        """
        Start the search using a board and a player as a starting state.
        :param on_find: A function that gets called everytime a better move is found.
        :param on_complete: A function that gets called when a search runs to exhaustion without
        interruption.
        """
