from datetime import datetime

from mmpy_bot import Message
from mmpy_bot import listen_to

from alarm.alarm_context import AlarmContextBuilder
from alarm.builtin.abstract_builtin_alarm import AbstractBuiltinAlarm
from common import constant


class JinhaAlarm(AbstractBuiltinAlarm):
    name = "진하"
    id = "jinha"
    day = "*"
    channel_id = constant.CH_JINHA_ID

    def __init__(self):
        super().__init__()
        self.add_builtin_alarm(self.name, self)

    def generate_message(self, option: str = ""):
        jinha_birth_day = datetime.strptime('2022-12-19', "%Y-%m-%d")
        now = datetime.now()

        year = str(int(now.strftime("%Y")))
        month = str(int(now.strftime("%m")))
        day = str(int(now.strftime("%d")))

        days_after_birth = (now - jinha_birth_day).days + 1

        age_year = days_after_birth / 365
        age_month = ((days_after_birth % 365) / 30).__str__()[:3]

        if age_year >= 3:
            age_str = "%d년 %s개월" % (age_year, age_month)
        else:
            age_str = "%s개월" % age_month

        msg = "@here `%s`\n오늘은 **진하**:baby:가 태어난지 %s일째(%s) 되는 날!" \
              % (now.strftime(year + "년 " + month + "월 " + day + "일"), days_after_birth, age_str)

        return msg

    @listen_to("^%s$" % name)
    def info(self, message: Message):
        self.driver.direct_message(message.user_id, self.generate_message())

    @listen_to("^%s알림$" % name)
    def notify(self, message: Message):
        self.alarm(self.channel_id)

    @listen_to(
        "^%s알람등록"
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)$"
        % name
    )
    def add_alarm(self, message: Message, hour: str, minute: str, recovery_mode: bool = False):
        alarm_context = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(self.channel_id) \
            .name(self.name).id(self.id) \
            .day(self.day).hour(hour).minute(minute) \
            .build()

        self.schedule_alarm(alarm_context, recovery_mode)

    @listen_to("^%s알람취소$" % name)
    def cancel_alarm(self, message: Message, post_to=channel_id):
        self.unschedule_alarm(self.name, self.id, message, post_to)
