from mmpy_bot import Message, Plugin, listen_to

from commons import constants
from commons.utils import get_alarms


class Alarms(Plugin):
    # 알람 정보 출력
    @listen_to("^알람목록$")
    def get_channel_alarms(self, message: Message):
        msg = get_alarms(constants.CHANNEL_ALARMS)

        self.driver.direct_message(message.user_id, msg)

    @listen_to("^개인알람목록$")
    def get_user_alarm(self, message: Message):
        msg = get_alarms(constants.USER_ALARMS, message.user_id)

        self.driver.direct_message(message.user_id, msg)
