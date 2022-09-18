import datetime

from mmpy_bot import Message
from mmpy_bot import listen_to

from commons import constant
from commons.alarm import Alarm


class KordleAlarm(Alarm):
    name = "꼬들"

    def __init__(self):
        self.id = "KordleAlarm"
        self.day = "mon-sun"
        self.ch = constant.CH_KORDLE_ID

    def generate_msg(self, option: str = ""):
        now = datetime.datetime.now()

        month = str(int(now.strftime("%m")))
        day = str(int(now.strftime("%d")))

        msg = "@here `" + now.strftime(month + "월 " + day + "일") + "`\n" \
              + "꼬들 한 번 풀어볼까요?!:zany_face:\n" \
              + "https://kordle.kr/"

        return msg

    @listen_to("^%s알림$" % name)
    def notify(self, message: Message):
        self.alarm(self.ch)

    @listen_to("^%s알림예약 (.+) (.+)$" % name)
    def add_alarm(self, message: Message, hour: str, minute: str):
        self.schedule_alarm(message, self.name, hour, minute)

    @listen_to("^%s알림예약취소$" % name)
    def cancel_alarm(self, message: Message):
        self.unschedule_alarm(self.name, message)
