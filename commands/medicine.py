from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

from commons import constant
from commons.alarm import Alarm


# 복약 메시지 생성
def generate_msg():
    msg = "@here 건강을 위해 **약** 먹을 시간 입니다! :pill::muscle:"

    return msg


class MedicineAlarm(Plugin):
    alarm_id: str = "MedicineAlarm"
    alarm_name: str = "복약"
    alarm_day: str = "mon-sun"
    alarm_text: str = generate_msg()

    # 복약 알림 예약
    @listen_to("^%s알림예약 ([1-9]|1[0-9]|2[0-4]) ([1-9]|1[0-9]|2[0-4]) ([0-9]|[1-5][0-9])$" % alarm_name)
    def add_alarm(self, message: Message, hour1: int, hour2: int, minute: int):
        # 기존에 등록된 알림 여부 확인
        job = constant.SCHEDULE.get_job(self.alarm_id)

        if job is not None:
            # 기존에 등록된 알림이 있는 경우, 기존 알림 정보 출력
            alarm: Alarm = constant.ALARMS.get(job.id)

            self.driver.direct_message(message.user_id,
                                       "이미 등록된 알림이 있습니다. `%s예약취소` 후 재등록 해주세요.\n"
                                       "**알림정보**\n"
                                       "%s\n"
                                       % (self.alarm_name, alarm.get_info()))
        else:
            # 기존에 등록된 작업이 없는 경우, 새로운 알림 등록 및 시작
            self.driver.direct_message(message.user_id, "`%s` 알림이 `%s %d:%02d, %d:%02d`에 전달됩니다." % (self.alarm_name, self.alarm_day, int(hour1), int(minute), int(hour2), int(minute)))
            constant.SCHEDULE.add_job(id=self.alarm_id,
                                      func=lambda: self.driver.create_post(constant.CH_NOTIFICATIONS_ID, generate_msg()),
                                      trigger='cron',
                                      day_of_week=self.alarm_day,
                                      hour=str(hour1) + ',' + str(hour2),
                                      minute=minute)

            job = constant.SCHEDULE.get_job(self.alarm_id)

            # 알림 정보 저장
            alarm = Alarm(message.sender_name, message.user_id, job.id, self.alarm_day, "%d:%02d, %d:%02d" % (int(hour1), int(minute), int(hour2), int(minute)))
            constant.ALARMS.update({job.id: alarm})

    # 예약 취소
    @listen_to("^%s알림예약취소$" % alarm_name)
    def cancel_alarm(self, message: Message):
        job = constant.SCHEDULE.get_job(self.alarm_id)

        if job is not None:
            # 알림 목록에서 취소할 알림의 정보를 불러와, 알림 생성자에게 삭제 내역 전달
            alarm: Alarm = constant.ALARMS.get(job.id)

            self.driver.direct_message(alarm.creator_id,
                                       "등록하신 `%s` 알림이 %s님에 의해 삭제되었습니다.\n\n"
                                       "**알림정보**\n"
                                       "%s\n"
                                       % (message.sender_name, self.alarm_name, alarm.get_info()))

            # 알림 리스트 및 백그라운드 스케쥴에서 제거
            constant.ALARMS.pop(job.id)
            constant.SCHEDULE.remove_job(job.id)

            self.driver.direct_message(message.user_id, "`%s` 알림이 종료되었습니다." % self.alarm_name)
        else:
            self.driver.direct_message(message.user_id, "등록된 알림이 없습니다.")
