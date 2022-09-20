from mmpy_bot import Message
from mmpy_bot import listen_to

from commons import constants
from commons.alarm import Alarm


class MedicineAlarm(Alarm):
    name = "복약"

    def __init__(self):
        self.id = "MedicineAlarm"
        self.day = "mon-sun"
        self.ch = constants.CH_NOTIFICATIONS_ID

    def generate_msg(self, option: str = ""):
        msg = "@here 건강을 위해 **약** 먹을 시간 입니다! :pill::muscle:"

        return msg

    # 복약 알림 예약
    @listen_to("^%s알림예약 (.+) (.+)$" % name)
    def add_alarm(self, message: Message, hour: str, minute: str):
        self.schedule_alarm(message, self.name, hour, minute)

    @listen_to("^%s알림예약취소$" % name)
    def cancel_alarm(self, message: Message):
        self.unschedule_alarm(self.name, message)
