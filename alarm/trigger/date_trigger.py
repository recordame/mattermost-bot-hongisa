import datetime

import urllib3
from apscheduler.triggers.base import BaseTrigger

urllib3.disable_warnings()


class CustomTrigger(BaseTrigger):
    __slots__ = 'hour', 'minute', 'second'

    def __init__(self, hour: int, minute: int, second: int):
        super().__init__()
        self.hour = hour
        self.minute = minute
        self.second = second

    def get_next_fire_time(self, previous_fire_time, now):
        if previous_fire_time:
            next_fire_time = previous_fire_time + datetime.timedelta(minutes=1)
        else:
            next_fire_time = now

        return next_fire_time
