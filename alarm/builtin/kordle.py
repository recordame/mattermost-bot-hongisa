import datetime

from mmpy_bot import listen_to, Message

from alarm.alarm_context import AlarmContextBuilder
from alarm.builtin.abstract_builtin_alarm import AbstractBuiltinAlarm
from common import constant


class KordleAlarm(AbstractBuiltinAlarm):
    name = '꼬들'
    id = 'kordle'
    day = 'mon-sun'
    channel_id = constant.CH_KORDLE_ID

    def __init__(self):
        super().__init__()
        self.add_builtin_alarm(self.name, self)

    def generate_message(self, option: str = ''):
        now = datetime.datetime.now()

        month = str(int(now.strftime('%m')))
        day = str(int(now.strftime('%d')))

        msg = '@here `' + now.strftime(month + '월 ' + day + '일') + '`\n' \
              + '꼬들 한 번 풀어볼까요?!:zany_face:\n' \
              + 'https://kordle.kr/'

        return msg

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
