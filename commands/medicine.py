from mmpy_bot import Message
from mmpy_bot import listen_to

from commons import constants
from commons.alarm import Alarm
from commons.alarm_context import AlarmContextBuilder


class MedicineAlarm(Alarm):
    name = "복약"
    id = "MedicineAlarm"
    day = "mon-sun"
    ch = constants.CH_NOTIFICATIONS_ID

    def generate_msg(self, option: str = ""):
        msg = "@here 건강을 위해 **약** 먹을 시간 입니다! :pill::muscle:"

        return msg

    # 복약 알람 예약
    @listen_to("^%s알람예약 (.+) (\\d+)$" % name)
    def add_alarm(self, message: Message, hour: str, minute: str, post_to=ch):
        alarm_context = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(post_to) \
            .name(self.name).id(self.id) \
            .day(self.day).hour(hour).minute(minute) \
            .build()

        self.schedule_alarm(alarm_context)

    @listen_to("^%s알람예약취소 (.+)$" % name)
    def cancel_alarm(self, message: Message, post_to=constants.CH_KORDLE_ID):
        self.unschedule_alarm(self.name, self.id, message, post_to)