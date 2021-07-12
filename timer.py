import time
import threading


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer(threading.Thread):
    def __init__(self):
        super().__init__()
        self._start_time = 10

    def start(self):
        """Start a new timer"""
        print("Starting")
        is_finished = False;
        curr_time = self._start_time
        while curr_time:
            if curr_time == 0:
                is_finished = True
                return is_finished
            print(curr_time)
            time.sleep(1)
            curr_time -= 1
        return is_finished

    def stop(self):
        """Stop the timer, and report the elapsed time"""


t = Timer()
run = True
while run:
    if not t.start():
        t.start()
    else:
        run = False


