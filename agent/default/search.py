import math
from time import sleep

from agent.state_generator import StateGenerator
from agent.heuristics.heuristic_jonathan import Heuristic
from ui.model.heuristic_type import HeuristicType
from core.board import Board
from core.color import Color
from core.constants import MAX_SELECTION_SIZE
from core.move import Move
from ui.debug import Debug, DebugType
import ui.constants

class Search:
    DEPTH_LIMIT = 2
    MIN = -math.inf
    MAX = math.inf

    def __init__(self):
        self.interrupt = False
        self.paused = False
        self.prune_count = 0
        self.node_count = 0
        self.heuristic_type = None
        self.on_find = None

    def set_heuristic_type(self, heuristic_type: HeuristicType):
        """
        Sets the heuristic type to be used by the search.
        :param heuristic_type: The heuristic type.
        """
        self.heuristic_type = heuristic_type

    def _get_heuristic(self, board: Board, player: Color):
        return self.heuristic_type.call(board, player)

    def alpha_beta(self, board: Board, player: Color, on_find: callable):
        """
        Search to find the best moves using minimax with alpha-beta pruning.
        """
        self.interrupt = False
        self.prune_count = 0
        self.node_count = 0
        self.on_find = on_find

        Debug.log(F"--- Search Start: {player} ---", DebugType.Agent)

        result = "Exhausted"
        try:
            self._alpha_beta_max(board, player, self.MIN, self.MAX,
                                 self.DEPTH_LIMIT, self.DEPTH_LIMIT)
        except TimeoutException:
            result = "Timeout"

        Debug.log(F"Result: {result}", DebugType.Agent)
        Debug.log(F"Heuristic: {self.heuristic_type.value}", DebugType.Agent)
        Debug.log(F"Branches Pruned: {self.prune_count}", DebugType.Agent)
        Debug.log(F"Nodes Searched: {self.node_count}", DebugType.Agent)

        Debug.log("--- Search Complete ---", DebugType.Agent)

    def _alpha_beta_max(self, board: Board, player: Color,
                        alpha: int, beta: int,
                        depth, depth_limit: int):
        """
        Alpha-beta helper function for the max player
        """
        if self.interrupt:
            raise TimeoutException()

        while self.paused:
            sleep(1 / ui.constants.FPS)

        if depth <= 0:
            self.node_count += 1
            return self._get_heuristic(board, player)

        best_heuristic = self.MIN

        moves = StateGenerator.enumerate_board(board, player)
        boards = StateGenerator.generate(board, moves)
        transitions = list(zip(moves, boards))

        if depth >= depth_limit:
            self._order_nodes(board, transitions)

        for index, node in enumerate(transitions):
            move, next_board = node

            if depth >= depth_limit:
                original_move = move

            heuristic = self._alpha_beta_min(next_board, player,
                                             alpha, beta,
                                             depth - 1, depth_limit)

            best_heuristic = max(best_heuristic, heuristic)

            if depth >= depth_limit:
                if best_heuristic > alpha:
                    Debug.log(F"Set Agent Move: {original_move}, {best_heuristic:0.4f}", DebugType.Agent)
                    self.on_find(original_move)

            if best_heuristic > beta:
                self.prune_count += len(transitions) - index
                return best_heuristic

            alpha = max(alpha, best_heuristic)

        return best_heuristic

    def _alpha_beta_min(self, board: Board, player: Color,
                        alpha: int, beta: int,
                        depth: int, depth_limit: int):
        """
        Alpha-beta helper function for the min player
        """
        if self.interrupt:
            raise TimeoutException()

        while self.paused:
            sleep(1 / ui.constants.FPS)

        if depth <= 0:
            self.node_count += 1
            return self._get_heuristic(board, player)

        best_heuristic = self.MAX

        moves = StateGenerator.enumerate_board(board, Color.next(player))
        boards = StateGenerator.generate(board, moves)

        for index, next_board in enumerate(boards):
            heuristic = self._alpha_beta_max(next_board, player,
                                             alpha, beta,
                                             depth - 1, depth_limit)

            best_heuristic = min(best_heuristic, heuristic)

            if best_heuristic < alpha:
                self.prune_count += len(boards) - index
                return best_heuristic

            beta = min(beta, best_heuristic)

        return best_heuristic

    @classmethod
    def _order_nodes(cls, board: Board, transitions: list[tuple[Move, Board]]):
        """
        Orders nodes based on their value
        """
        transitions.sort(key=lambda transition: cls._order_move(transition[0], board), reverse=True)

    @staticmethod
    def _order_move(move: Move, board: Board):
        """
        Gets a comparison value for a move, ordered by sumitos and then move selection size.
        """
        if move.is_sumito(board):
            return MAX_SELECTION_SIZE + 1
        return len(move.get_cells())

    def _alpha_beta_old(self, depth, first_layer_index, is_max, board, alpha, beta, player, on_find):
        # Minimax with alpha-beta pruning
        # depth is reached
        if depth > self.DEPTH_LIMIT:
            return Heuristic.main(board, player)  # HEURISTIC GOES HERE
        if is_max:
            # MAX
            best_value = self.MIN
            moves = StateGenerator.enumerate_board(board, player)
            # Node orders if this is the first layer of boards.
            if not self.node_ordered_yet:
                self.node_ordered_yet = True
                deeper_boards = self._order_nodes(StateGenerator.generate(board, moves))
            else:
                deeper_boards = StateGenerator.generate(board, moves)

            # for all children of the board
            for i in range(0, len(deeper_boards)):
                if depth == 0:
                    first_layer_index = i
                    print(F"{moves[first_layer_index]}, {Heuristic.main(deeper_boards[i], player)}")
                current_value = self._alpha_beta_old(depth + 1, first_layer_index, False, deeper_boards[i], alpha, beta, player, on_find)
                if current_value > best_value:
                    best_value = current_value
                    # stores best move so far inside class variable.
                    self.best_move = first_layer_index
                    on_find(self.moves[self.best_move])
                alpha = max(alpha, best_value)
                # pruning
                if beta <= alpha:
                    break
            return best_value
        else:
            # MIN
            best_value = self.MAX
            moves = StateGenerator.enumerate_board(board, Color.next(player))
            deeper_boards = StateGenerator.generate(board, moves)
            # for all children of the board
            for i in range(0, len(deeper_boards)):
                current_value = self._alpha_beta_old(depth + 1, first_layer_index, True, deeper_boards[i], alpha, beta, player, on_find)
                best_value = min(best_value, current_value)
                beta = min(beta, best_value)
                # pruning
                if beta <= alpha:
                    break
            return best_value


class TimeoutException(Exception):
    """
    Timeout exception to cancel search in progress.
    """
    pass
