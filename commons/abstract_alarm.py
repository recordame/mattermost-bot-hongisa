import json
from abc import *

from mmpy_bot import Message
from mmpy_bot import Plugin

from commons import constant
from commons.alarm_context import AlarmContext


class AbstractAlarm(Plugin, metaclass=ABCMeta):
    id: str
    day: str
    ch: str

    @abstractmethod
    def generate_msg(self, param: str = ""):
        print(param)
        return "alarm message"

    @abstractmethod
    def add_alarm(self, message: Message, hour: str, minute: str):
        self.schedule_alarm(message, hour, minute)

    @abstractmethod
    def cancel_alarm(self, message: Message):
        alarm_name = "alarm name"
        self.unschedule_alarm(alarm_name, message)

    def alarm(self, recipient: str, is_post: bool = True, msg_para: str = ""):
        if is_post:
            self.driver.create_post(recipient, self.generate_msg(msg_para))
        else:
            self.driver.direct_message(recipient, self.generate_msg(msg_para))

    def is_already_scheduled(self, alarm_id, alarm_name, message: Message):
        job = constant.SCHEDULE.get_job(alarm_id)

        if job is not None:
            # 기존에 등록된 알림이 있는 경우, 기존 알림 정보 출력
            alarm_ctx: AlarmContext = constant.ALARMS.get(job.id)

            self.driver.direct_message(message.user_id,
                                       "이미 등록된 알림이 있습니다. `%s알림예약취소` 후 재등록 해주세요.\n"
                                       "**알림정보**\n"
                                       "%s\n"
                                       % (alarm_name, alarm_ctx.get_info()))
            return True
        else:
            return False

    def schedule_alarm(self, message: Message, alarm_name: str, hour: str, minute: str, msg_param: str = ""):
        if self.is_already_scheduled(self.id, alarm_name, message) is False:
            # 기존에 등록된 작업이 없는 경우, 새로운 알림 등록 및 시작
            self.driver.direct_message(message.user_id, "`%s` 알림이 `%s %s:%02d`에 전달됩니다." % (alarm_name, self.day, hour, int(minute)))

            constant.SCHEDULE.add_job(id=self.id,
                                      func=lambda: self.alarm(self.ch, msg_param),
                                      trigger='cron',
                                      day_of_week=self.day,
                                      hour=hour,
                                      minute=minute)

            job = constant.SCHEDULE.get_job(self.id)

            # 알림 정보 저장
            alarm_ctx = AlarmContext(message.sender_name, message.user_id, job.id, self.day, "%s:%02d" % (hour, int(minute)), msg_param=msg_param)
            constant.ALARMS.update({job.id: alarm_ctx})

            # 알림정보 파일 저장
            alarm_db = open('./alarms', 'w', encoding='UTF-8')

            alarm_db.write('[')

            i = 0
            cnt = constant.ALARMS.values().__len__()
            key = list(constant.ALARMS.keys())

            while i < cnt:
                json.dump(constant.ALARMS.get(key[i]).__dict__, alarm_db, indent=4)

                i += 1

                if i < cnt:
                    alarm_db.write(',\n')

            alarm_db.write(']')
            alarm_db.close()

    def unschedule_alarm(self, alarm_name, message: Message):
        job = constant.SCHEDULE.get_job(self.id)

        if job is not None:
            # 알림 목록에서 취소할 알림의 정보를 불러와, 알림 생성자에게 삭제 내역 전달
            alarm_ctx: AlarmContext = constant.ALARMS.get(job.id)

            self.driver.direct_message(alarm_ctx.creator_id,
                                       "등록하신 `%s` 알림이 %s님에 의해 삭제되었습니다.\n\n"
                                       "**알림정보**\n"
                                       "%s\n"
                                       % (message.sender_name, alarm_name, alarm_ctx.get_info()))

            # 알림 리스트 및 백그라운드 스케쥴에서 제거
            constant.ALARMS.pop(job.id)
            constant.SCHEDULE.remove_job(job.id)

            self.driver.direct_message(message.user_id, "`%s` 알림이 종료되었습니다." % alarm_name)
        else:
            self.driver.direct_message(message.user_id, "등록된 알림이 없습니다.")
