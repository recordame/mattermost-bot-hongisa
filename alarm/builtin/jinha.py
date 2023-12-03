from datetime import datetime

from mmpy_bot import listen_to, Message

from alarm.alarm_context import AlarmContextBuilder
from alarm.builtin.abstract_builtin_alarm import AbstractBuiltinAlarm
from common import constant


class JinhaAlarm(AbstractBuiltinAlarm):
    name = '진하'
    id = 'jinha'
    day = '*'
    channel_id = constant.CH_JINHA_ID

    def __init__(self):
        super().__init__()
        self.add_builtin_alarm(self.name, self)

    def generate_message(self, option: str = ''):
        jinha_birth_day = datetime(2022, 12, 19)
        today = datetime.now()
        days_after_birth = (today - jinha_birth_day).days + 1

        month_count = 0
        days_count = 0
        for year in range(2023, today.year + 1):
            for month in range(1, 13):
                if datetime(year, month, 19) < datetime(today.year, today.month, today.day):
                    month_count += 1
                else:
                    days_count = (datetime(today.year, today.month, today.day) - datetime(year, month - 1, 19)).days + 1

        age_year = month_count / 12
        age_month = month_count
        age_day = days_count

        if age_year >= 3:
            age_str = '%d년 %s개월' % (age_year, age_month)
        else:
            age_str = '%s개월 %s일' % (age_month, age_day)

        msg = '@here `%s`\n오늘은 **진하**:baby:가 태어난지 %s일째(%s) 되는 날!' \
              % (today.strftime('%Y년 %m월 %d일'), days_after_birth, age_str)

        return msg

    @listen_to('^%s$' % name)
    def info(self, message: Message):
        self.driver.direct_message(message.user_id, self.generate_message())

    @listen_to('^%s알림$' % name)
    def notify(self, message: Message):
        self.alarm(self.channel_id)

    @listen_to(
        '^%s알람등록'
        '\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)'
        '\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)$'
        % name
    )
    def add_alarm(self, message: Message, hour: str, minute: str, recovery_mode: bool = False):
        alarm_context = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(self.channel_id) \
            .name(self.name).id(self.id) \
            .day(self.day).hour(hour).minute(minute) \
            .build()

        self.schedule_alarm(alarm_context, recovery_mode)

    @listen_to('^%s알람취소$' % name)
    def cancel_alarm(self, message: Message, post_to=channel_id):
        self.unschedule_alarm(self.name, self.id, message, post_to)
