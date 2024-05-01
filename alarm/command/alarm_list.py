import logging

import mmpy_bot

from alarm.alarm_util import get_alarm_info, count_alarms
from common import constant


class AlarmList(mmpy_bot.Plugin):
    @mmpy_bot.listen_to('^알람통계$', allowed_users=constant.ADMINS, direct_only=True)
    def get_alarm_counts(self, message: mmpy_bot.Message):
        msg: str = ''

        count = count_alarms(constant.CHANNEL_ALARMS)
        msg += f'- 채널: {count}개\n'

        count = count_alarms(constant.USER_ALARMS)
        msg += f'- 개인: {count}개\n'

        count = count_alarms(constant.EPHEMERAL_ALARMS)
        msg += f'- 예약: {count}개\n'

        self.driver.direct_message(message.user_id, msg)

    @mmpy_bot.listen_to('^알람목록(\\s(.+))?$', direct_only=True)
    def get_all_alarms_by_creator_id(self, message: mmpy_bot.Message, dummy, channel_id: str = None):
        logging.info('[stat] 알람목록')

        msg: str = '----\n\n'
        msg = msg + get_alarm_info('채널', constant.CHANNEL_ALARMS, channel_id, message.user_id)
        self.driver.reply_to(message, msg)

        if channel_id is None:
            msg = '----\n\n'
            msg = msg + get_alarm_info('개인', constant.USER_ALARMS, channel_id, message.user_id)
            self.driver.reply_to(message, msg)

        msg = '----\n\n'
        msg = msg + get_alarm_info('예약', constant.EPHEMERAL_ALARMS, channel_id, message.user_id)
        self.driver.reply_to(message, msg)
