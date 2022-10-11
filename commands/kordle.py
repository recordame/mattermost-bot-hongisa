import datetime

from mmpy_bot import Message
from mmpy_bot import listen_to

from commons import constants
from commons.alarm import Alarm
from commons.alarm_context import AlarmContextBuilder


class KordleAlarm(Alarm):
    name = "꼬들"
    id = "kordle"
    day = "mon-sun"
    channel_id = constants.CH_KORDLE_ID

    def generate_message(self, option: str = ""):
        now = datetime.datetime.now()

        month = str(int(now.strftime("%m")))
        day = str(int(now.strftime("%d")))

        msg = "@here `" + now.strftime(month + "월 " + day + "일") + "`\n" \
              + "꼬들 한 번 풀어볼까요?!:zany_face:\n" \
              + "https://kordle.kr/"

        return msg

    @listen_to("^%s알림$" % name)
    def notify(self, message: Message, post_to=channel_id):
        self.alarm("to_channel", post_to)

    @listen_to("^%s알람예약 (.+) (\\d+)$" % name)
    def add_alarm(self, message: Message, hour: str, minute: str, post_to=channel_id):
        alarm_context = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(post_to) \
            .name(self.name).id(self.id) \
            .day(self.day).hour(hour).minute(minute) \
            .build()

        self.schedule_alarm(alarm_context)

    @listen_to("^%s알람취소$" % name)
    def cancel_alarm(self, message: Message, post_to=channel_id):
        self.unschedule_alarm(self.name, self.id, message, post_to)
