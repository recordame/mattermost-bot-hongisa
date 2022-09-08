from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

from commons import constant
from commons.alarm import Alarm


# 복약 메시지 생성
def generate_msg():
    msg = "@here 건강을 위해 **약** 먹을 시간 입니다! :pill::muscle:"

    return msg


class MedicineAlarm(Plugin):
    schedule = BackgroundScheduler()

    # 복약 알림 예약
    @listen_to("^복약알림예약 ([1-9]|1[0-9]|2[0-4]) ([1-9]|1[0-9]|2[0-4]) ([0-9]|[1-5][0-9])$")
    def add_alarm(self, message: Message, hour1: int, hour2: int, minute: int):
        if self.schedule.get_jobs().__len__() == 1:
            # 기존에 등록된 알림이 있는 경우, 기존 알림 정보 출력
            job = self.schedule.get_jobs()[0]
            alarm: Alarm = constant.ALARMS.get(job.id)

            self.driver.direct_message(message.user_id,
                                       "이미 등록된 알림이 있습니다. `약복용예약취소` 후 재등록 해주세요.\n\n"
                                       "**알림정보**\n" + alarm.get_info() + "\n"
                                       )
        else:
            # 기존에 등록된 작업이 없는 경우, 새로운 알림 등록 및 시작
            self.driver.direct_message(message.user_id, "복약 알림이 매일 `%d:%02d, %d:%02d`에 전달됩니다." % (int(hour1), int(minute), int(hour2), int(minute)))
            self.schedule.add_job(func=lambda: self.driver.create_post(constant.CH_NOTIFICATIONS_ID, generate_msg()),
                                  trigger='cron',
                                  day_of_week='mon-sun',
                                  hour=str(hour1) + ',' + str(hour2),
                                  minute=minute)

            self.schedule.start()

            # 알림 정보 저장
            job = self.schedule.get_jobs()[0]
            alarm = Alarm(message.sender_name, message.user_id, job, "mon-sun", "%d:%02d, %d:%02d" % (int(hour1), int(minute), int(hour2), int(minute)))
            constant.ALARMS.update({job.id: alarm})

    # 예약 취소
    @listen_to("^복약알림예약취소$")
    def cancel_alarm(self, message: Message):
        # 알림 목록에서 취소할 알림의 정보를 불러와, 알림 생성자에게 삭제 내역 전달
        job = self.schedule.get_jobs()[0]
        alarm: Alarm = constant.ALARMS.get(job.id)
        self.driver.direct_message(alarm.creator_id, "등록하신 복약 알림이 %s님에 의해 삭제되었습니다. \n\n"
                                   % (message.sender_name) + "**알림정보**\n" + alarm.get_info() + "\n")

        # 알림 종료 및 알림 리스트에서 제거
        constant.ALARMS.pop(job.id)

        self.schedule.shutdown()
        self.driver.direct_message(message.user_id, "복약 알림이 종료되었습니다.")
        # 다음 스케쥴 등록을 위해 새로운 스케쥴러 생성
        self.schedule = BackgroundScheduler()
