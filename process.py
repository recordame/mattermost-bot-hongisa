from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


class Process(Plugin):
    schedule = BackgroundScheduler()

    @listen_to("^프로세스정보$")
    def notify(self, message: Message):
        msg: str = ""

        for i in constant.JOBS:
            msg += "``" + str(i) + "``\n"

        self.driver.direct_message(message.user_id, "현재 백그라운드에서 작동중인 스케쥴러 : " + str(constant.JOBS.__len__()) + "개\n" + msg)
