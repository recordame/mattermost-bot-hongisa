from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


class Process(Plugin):

    # 프로세스 정보 출력
    @listen_to("^프로세스$")
    def notify(self, message: Message):
        msg: str = ""

        for i in constant.JOBS:
            msg += "``" + str(i) + "``\n"

        self.driver.direct_message(message.user_id, "Background Jobs : " + str(constant.JOBS.__len__()) + "개\n" + msg)
