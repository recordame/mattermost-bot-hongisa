import datetime


from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to


# 꼬들 메시지 생성
from commons import constant
from commons.alarm import Alarm


def generate_msg():
    now = datetime.datetime.now()

    month = str(int(now.strftime("%m")))
    day = str(int(now.strftime("%d")))

    msg = "@here `" + now.strftime(month + "월 " + day + "일") + "`\n" \
          + "꼬들 한 번 풀어볼까요?!:zany_face:\n" \
          + "https://kordle.kr/"

    return msg


class KordleAlarm(Plugin):
    schedule = BackgroundScheduler()

    # 전체공유
    @listen_to("^꼬들알림$")
    def notify(self, message: Message):
        self.driver.create_post(constant.CH_KORDLE_ID, generate_msg())

    # 꼬들 알림 예약
    @listen_to("^꼬들알림예약 ([1-9]|1[0-9]|2[0-4]) ([1-9]|[1-5][0-9])$")
    def add_alarm(self, message: Message, hour: int, minute: int):
        if self.schedule.get_jobs().__len__() == 1:
            # 기존에 등록된 알림이 있는 경우, 기존 알림 정보 출력
            job = self.schedule.get_jobs()[0]
            alarm: Alarm = constant.ALARMS.get(job.id)

            self.driver.direct_message(message.user_id,
                                       "이미 등록된 알림이 있습니다. `꼬들예약취소` 후 재등록 해주세요.\n\n"
                                       "**알림정보**\n" + alarm.get_info() + "\n"
                                       )
        else:
            # 기존에 등록된 작업이 없는 경우, 새로운 알림 등록 및 시작
            self.driver.direct_message(message.user_id, "꼬들 알림이 매일 `%d:%02d`에 전달됩니다." % (int(hour), int(minute)))
            self.schedule.add_job(func=lambda: self.driver.create_post(constant.CH_KORDLE_ID, generate_msg()),
                                  trigger='cron',
                                  day_of_week='mon-sun',
                                  hour=hour,
                                  minute=minute)

            self.schedule.start()

            # 알림 정보 저장
            job = self.schedule.get_jobs()[0]
            alarm = Alarm(message.sender_name, message.user_id, job, "mon-sun", "%d:%02d" % (int(hour), int(minute)))
            constant.ALARMS.update({job.id: alarm})

    # 꼬들 예약 취소
    @listen_to("^꼬들알림예약취소$")
    def cancel_alarm(self, message: Message):
        # 알림 목록에서 취소할 알림의 정보를 불러와, 알림 생성자에게 삭제 내역 전달
        job = self.schedule.get_jobs()[0]
        alarm: Alarm = constant.ALARMS.get(job.id)
        self.driver.direct_message(alarm.creater_id, "등록하신 꼬들 알림이 %s님에 의해 삭제되었습니다. \n\n"
                                   % (message.sender_name) + "**알림정보**\n" + alarm.get_info() + "\n")

        # 알림 종료 및 알림 리스트에서 제거
        constant.ALARMS.pop(job.id)

        self.schedule.shutdown()
        self.driver.direct_message(message.user_id, "꼬들 알림이 종료되었습니다.")
        # 다음 스케쥴 등록을 위해 새로운 스케쥴러 생성
        self.schedule = BackgroundScheduler()
