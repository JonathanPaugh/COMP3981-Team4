from abc import ABC, abstractmethod

from ui.model.heuristic_type import HeuristicType
from core.board import Board
from core.color import Color


class BaseAgent(ABC):
    """
    An abstract class for an Abalone agent.
    """

    @abstractmethod
    def start(self, board: Board, player: Color, on_find: callable, on_complete: callable):
        """
        Start the search using a board and a player as a starting state.
        :param on_find: A function that gets called everytime a better move is found.
        :param on_complete: A function that gets called when a search runs to exhaustion without
        interruption.
        """

    @abstractmethod
    def stop(self):
        """
        Force the search to stop.
        """

    @abstractmethod
    def toggle_paused(self):
        """
        Pauses or resumes the search based on the pause state.
        """

    @abstractmethod
    def set_heuristic_type(self, heuristic_type: HeuristicType):
        """
        Sets the heuristic to be used by the search.
        :param heuristic_type: The heuristic type.
        """