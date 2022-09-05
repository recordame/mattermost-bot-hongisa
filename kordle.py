import datetime

import schedule
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


class Kordle(Plugin):
    @listen_to("^꼬들$")
    def kordle(self, message: Message):
        now = datetime.datetime.now()

        msg = "@here\n" \
              + "**" + now.strftime("%m월 %d일") + "**" \
              + " 꼬들 한 번 풀어볼까요?!\n" \
              + "https://kordle.kr/"

        self.driver.create_post(constant.CH_KORDLE_ID, msg)

    @listen_to("^꼬들시작 (1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24)$")
    def kordle_alarm(self, message: Message, at: str):
        oclock: str = str('{:02d}'.format(int(at))) + ":00"

        now = datetime.datetime.now()

        msg = "@here\n" \
              + "**" + now.strftime("%m월 %d일") + "**" \
              + " 꼬들 한 번 풀어볼까요?!\n" \
              + "https://kordle.kr/"

        self.driver.direct_message(message.user_id, "꼬들 알림이 매일 " + oclock + "시에 전달됩니다.")

        schedule.every().day.at(oclock).do(
            self.driver.create_post, constant.CH_KORDLE_ID, msg
        )

    @listen_to("^꼬들종료$")
    def cancel_jobs(self, message: Message):
        schedule.clear()

        self.driver.direct_message(message.user_id, "꼬들 알림이 종료되었습니다.")
