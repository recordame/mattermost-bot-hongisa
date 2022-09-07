from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


class Alarms(Plugin):

    # 알람 정보 출력
    @listen_to("^알림목록$")
    def notify(self, message: Message):
        msg: str = ""

        for alarm in constant.ALARMS.values():
            msg += "[알림]\n" + alarm.get_info() + "\n"

        self.driver.direct_message(message.user_id,
                                   "등록된 알림 : %d 개\n" % (constant.ALARMS.__len__()) + msg + "\n")
