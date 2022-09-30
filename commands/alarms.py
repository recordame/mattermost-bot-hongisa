from commons import constants
from mmpy_bot import Message, Plugin, listen_to


class Alarms(Plugin):
    # 알람 정보 출력
    @listen_to("^알람목록$")
    def get_alarms(self, message: Message):
        msg: str = ""

        for alarm in constants.ALARMS.values():
            msg += "[알람]\n" + alarm.get_info() + "\n"

        self.driver.direct_message(
            message.user_id,
            "등록된 알람 : %d 개\n" % (constants.ALARMS.__len__()) + msg + "\n")
