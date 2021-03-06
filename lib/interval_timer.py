import threading
import time
from lib.clamp import clamp_01
import ui.constants


class IntervalTimer(threading.Thread):
    def __init__(self, total_time: float, interval: float):
        super().__init__()
        self.daemon = True
        self.interrupted = False
        self.paused = False
        self.stopped = threading.Event()

        self.total_time = total_time
        self.interval = interval

        self.on_interval = None
        self.on_complete = None

    @property
    def remaining_time(self):
        return

    def set_on_complete(self, on_complete):
        self.on_complete = on_complete

    def set_on_interval(self, on_interval):
        self.on_interval = on_interval

    def stop(self):
        self.interrupted = True
        self.stopped.set()
        self.join()

    def toggle_pause(self):
        self.paused = not self.paused

    def run(self):
        remaining_time = self.total_time

        start_time = time.time()
        while remaining_time > 0 and not self.stopped.wait(self.interval): # Time resolution is really bad
            if self.on_interval:
                self.on_interval(self._get_progress(remaining_time))
            end_time = time.time()
            remaining_time -= end_time - start_time

            while self.paused and not self.stopped.is_set():
                self.stopped.wait(1 / ui.constants.FPS)

            start_time = time.time()

        if self.on_complete and not self.interrupted:
            self.on_interval(0)
            self.on_complete()

    def _get_progress(self, remaining_time):
        return clamp_01(remaining_time / self.total_time)