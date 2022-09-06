import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


# 꼬들 메시지 생성
def generate_msg():
    now = datetime.datetime.now()

    month = str(int(now.strftime("%m")))
    day = str(int(now.strftime("%d")))

    msg = "@here ``" + now.strftime(month + "월 " + day + "일") + "``\n" \
          + "꼬들 한 번 풀어볼까요?!:zany_face:\n" \
          + "https://kordle.kr/"

    return msg


class Kordle(Plugin):
    schedule = BackgroundScheduler()

    # 전체공유
    @listen_to("^꼬들알림$")
    def notify(self, message: Message):
        self.driver.create_post(constant.CH_KORDLE_ID, generate_msg())

    # 꼬들 알림 예약
    @listen_to("^꼬들예약 ([1-9]|1[0-9]|2[0-4]) ([0-5][0-9])$")
    def add_alarm(self, message: Message, at1: int, at2: int):
        self.schedule.add_job(func=lambda: self.driver.create_post(constant.CH_KORDLE_ID, generate_msg()),
                              trigger='cron',
                              day_of_week='mon-sun',
                              hour=at1,
                              minute=at2)

        oclock: str = str(at1) + ":" + str('{:02d}'.format(int(at2)))
        self.driver.direct_message(message.user_id, "꼬들 알림이 매일 ``" + oclock + "``에 전달됩니다.")

        self.schedule.start()
        constant.JOBS.append(self.schedule.get_jobs())


    # 꼬들 예약 취소
    @listen_to("^꼬들예약취소$")
    def cancel_alarm(self, message: Message):
        print(self.schedule.get_jobs())
        constant.JOBS.remove(self.schedule.get_jobs())
        self.schedule.shutdown()
        self.driver.direct_message(message.user_id, "꼬들 알림이 종료되었습니다.")
