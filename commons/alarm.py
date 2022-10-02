from abc import ABCMeta, abstractmethod

from mmpy_bot import Message
from mmpy_bot import Plugin

from commons import constants
from commons.alarm_context import AlarmContext
from commons.utils import save_channel_alarms_to_file_in_json


class Alarm(Plugin, metaclass=ABCMeta):
    id: str
    day: str
    ch: str

    @abstractmethod
    def generate_msg(self, param: str = ""):
        print(param)
        return "alarm message"

    @abstractmethod
    def add_alarm(self, message: Message, hour: str, minute: str):
        self.schedule_alarm(message=message, alarm_name="", hour=hour, minute=minute)

    @abstractmethod
    def cancel_alarm(self, message: Message):
        alarm_name = "alarm name"
        self.unschedule_alarm(alarm_name=alarm_name, message=message)

    def alarm(self, recipient: str, is_post: bool = True, msg_param: str = ""):
        if is_post:
            self.driver.create_post(recipient, self.generate_msg(msg_param))
        else:
            self.driver.direct_message(recipient, self.generate_msg(msg_param))

    def schedule_alarm(self,
                       message: Message,
                       alarm_name: str,
                       hour: str,
                       minute: str,
                       msg_param: str = ""):

        if self.is_already_scheduled(self.id, alarm_name, message) is False:
            # 기존에 등록된 작업이 없는 경우, 새로운 알람 등록 및 시작
            self.driver.direct_message(
                message.user_id, "`%s` 알람이 `%s %s:%02d`에 전달됩니다." %
                                 (alarm_name, self.day, hour, int(minute)))

            constants.SCHEDULE.add_job(
                id=self.id,
                func=lambda: self.alarm(self.ch, is_post=True, msg_param=msg_param),
                trigger='cron',
                day_of_week=self.day,
                hour=hour,
                minute=minute,
                misfire_grace_time=10
            )

            job = constants.SCHEDULE.get_job(self.id)

            # 알람 정보 저장
            alarm_ctx = AlarmContext(message.sender_name,
                                     message.user_id,
                                     job.id,
                                     self.day,
                                     "%s:%02d" % (hour, int(minute)),
                                     msg_param=msg_param)
            constants.ALARMS.update({job.id: alarm_ctx})

            save_channel_alarms_to_file_in_json()

    def is_already_scheduled(self, alarm_id, alarm_name, message: Message):
        job = constants.SCHEDULE.get_job(alarm_id)

        if job is not None:
            # 기존에 등록된 알람이 있는 경우, 기존 알람 정보 출력
            alarm_ctx: AlarmContext = constants.ALARMS.get(job.id)

            self.driver.direct_message(
                message.user_id, "이미 등록된 알람이 있습니다. `%s알람예약취소` 후 재등록 해주세요.\n"
                                 "**알람정보**\n"
                                 "%s\n" % (alarm_name, alarm_ctx.get_info()))
            return True
        else:
            return False

    def unschedule_alarm(self, alarm_name, message: Message):
        job = constants.SCHEDULE.get_job(self.id)

        if job is not None:
            # 알람 목록에서 취소할 알람의 정보를 불러와, 알람 생성자에게 삭제 내역 전달
            alarm_ctx: AlarmContext = constants.ALARMS.get(job.id)

            self.driver.direct_message(
                alarm_ctx.creator_id, "등록하신 `%s` 알람이 %s님에 의해 삭제되었습니다.\n\n"
                                      "**알람정보**\n"
                                      "%s\n" %
                                      (message.sender_name, alarm_name, alarm_ctx.get_info()))

            # 알람 리스트 및 백그라운드 스케쥴에서 제거
            constants.ALARMS.pop(job.id)
            constants.SCHEDULE.remove_job(job.id)

            self.driver.direct_message(message.user_id,
                                       "`%s` 알람이 종료되었습니다." % alarm_name)

            save_channel_alarms_to_file_in_json()
        else:
            self.driver.direct_message(message.user_id, "등록된 알람이 없습니다.")
