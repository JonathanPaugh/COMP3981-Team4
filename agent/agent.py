from __future__ import annotations
from typing import TYPE_CHECKING

from agent.agent_thread import AgentThread
from agent.search import Search

if TYPE_CHECKING:
    from core.board import Board
    from core.color import Color


class Agent:
    def __init__(self):
        self._search = Search()
        self._thread = None

    def search(self, board: Board, player: Color, on_find: callable):
        self._launch_thread(board, player, on_find)

    def stop(self):
        if self._thread:
            self._thread.stop()
        self._thread = None

    def _launch_thread(self, board: Board, player: Color, on_find_move: callable):
        if self._thread and self._thread.is_alive():
            self._thread.stop()
            raise Exception("Agent thread attempted to start while previous thread still alive")

        self._thread = AgentThread(self._search, board, player, on_find_move)
        self._thread.start()
