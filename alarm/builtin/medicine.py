from mmpy_bot import listen_to, Message

from alarm.alarm_context import AlarmContextBuilder
from alarm.builtin.abstract_builtin_alarm import AbstractChannelAlarm
from common import constant


class MedicineAlarm(AbstractChannelAlarm):
    name = '복약'
    id = 'medicine'
    day = 'mon-sun'
    channel_id = constant.CH_NOTIFICATIONS_ID

    def __init__(self):
        super().__init__()
        self.register_instance(self.name, self)

    def generate_message(self, option: str = ''):
        msg = '@here 건강을 위해 **약** 먹을 시간 입니다! :pill::muscle:'

        return msg

    # 복약 알람 예약
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
