import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


def generate_msg():
    now = datetime.datetime.now()

    month = str(int(now.strftime("%m")))
    day = str(int(now.strftime("%d")))

    msg = "@here ``" + now.strftime(month + "월 " + day + "일") + "``\n" \
          + "꼬들 한 번 풀어볼까요?!:zany_face:\n" \
          + "https://kordle.kr/"

    return msg


class Kordle(Plugin):
    schedule = BlockingScheduler()

    @listen_to("^꼬들알림$")
    def kordle(self, message: Message):
        self.driver.create_post(constant.CH_KORDLE_ID, generate_msg())

    @listen_to("^꼬들알림시작 (1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24) (1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24)$")
    def kordle_alarm(self, message: Message, at1: str, at2: str):
        self.schedule.add_job(lambda: self.driver.create_post(constant.CH_KORDLE_ID, generate_msg()), trigger='cron', day_of_week='mon-sun', hour=int(at1), minute=int(at2))

        oclock: str = str('{:02d}'.format(int(at1))) + ":" + str('{:02d}'.format(int(at2)))
        self.driver.direct_message(message.user_id, "꼬들 알림이 매일 ``" + oclock + "``에 전달됩니다.")

        self.schedule.start()

    @listen_to("^꼬들알림종료$")
    def cancel_jobs(self, message: Message):
        self.schedule.shutdown()
        self.driver.direct_message(message.user_id, "꼬들 알림이 종료되었습니다.")
