from mmpy_bot import Message, Plugin, listen_to

from alarm.alarm_util import get_alarms
from common import constant


class Alarms(Plugin):
    # 알람 정보 출력
    @listen_to('^알람목록$')
    def get_alarms(self, message: Message):
        msg = get_alarms('채널', constant.CHANNEL_ALARMS)
        self.driver.direct_message(message.user_id, msg)

        msg = get_alarms('개인', constant.USER_ALARMS)
        self.driver.direct_message(message.user_id, msg)

    @listen_to('^채널알람목록$')
    def get_channel_alarms(self, message: Message):
        msg = get_alarms('채널', constant.CHANNEL_ALARMS)
        self.driver.direct_message(message.user_id, msg)

    @listen_to('^개인알람목록$')
    def get_user_alarms(self, message: Message):
        msg = get_alarms('개인', constant.USER_ALARMS)
        self.driver.direct_message(message.user_id, msg)
