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
    alarm_id: str = "KordleAlarm"
    alarm_name: str = "꼬들"
    alarm_day: str = "mon-sun"
    alarm_text: str = generate_msg()

    # 전체공유
    @listen_to("^%s알림$" % alarm_name)
    def notify(self, message: Message):
        self.driver.create_post(constant.CH_KORDLE_ID, self.alarm_text)

    # 꼬들 알림 예약
    @listen_to("^%s알림예약 ([1-9]|1[0-9]|2[0-4]) ([1-9]|[1-5][0-9])$" % alarm_name)
    def add_alarm(self, message: Message, hour: int, minute: int):
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
            self.driver.direct_message(message.user_id, "`%s` 알림이 `%s %d:%02d`에 전달됩니다." % (self.alarm_name, self.alarm_day, int(hour), int(minute)))
            constant.SCHEDULE.add_job(id=self.alarm_id,
                                      func=lambda: self.driver.create_post(constant.CH_KORDLE_ID, generate_msg()),
                                      trigger='cron',
                                      day_of_week=self.alarm_day,
                                      hour=hour,
                                      minute=minute)

            job = constant.SCHEDULE.get_job(self.alarm_id)

            # 알림 정보 저장
            alarm = Alarm(message.sender_name, message.user_id, job.id, self.alarm_day, "%d:%02d" % (int(hour), int(minute)))
            constant.ALARMS.update({job.id: alarm})

    # 꼬들 예약 취소
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
