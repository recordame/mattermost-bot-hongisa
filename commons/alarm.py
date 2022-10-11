from abc import ABCMeta, abstractmethod

from mmpy_bot import Message
from mmpy_bot import Plugin

from commons import constants
from commons.alarm_context import AlarmContext
from commons.utils import save_alarms_to_file_in_json


class Alarm(Plugin, metaclass=ABCMeta):
    @abstractmethod
    def generate_message(self, param: str = ""):
        pass

    @abstractmethod
    def add_alarm(self, message: Message, hour: str, minute: str):
        pass

    @abstractmethod
    def cancel_alarm(self, message: Message):
        pass

    def alarm(self, alarm_type: str, post_to: str, message_argument: str = ""):
        if alarm_type == "to_channel":
            self.driver.create_post(post_to, self.generate_message(message_argument))
        elif alarm_type == "to_user":
            self.driver.direct_message(post_to, self.generate_message(message_argument))

    def schedule_alarm(self, ctx: AlarmContext):
        if self.is_alarm_already_scheduled(ctx) is False:
            channel_alarms = constants.CHANNEL_ALARMS.get(ctx.post_to)

            if channel_alarms is not None:
                constants.CHANNEL_ALARMS[ctx.post_to].update({ctx.id: ctx})
            else:
                constants.CHANNEL_ALARMS.update({ctx.post_to: {ctx.id: ctx}})

            constants.CHANNEL_ALARM_SCHEDULE.add_job(
                id=ctx.job_id,
                func=lambda: self.alarm("to_channel", ctx.post_to, message_argument=ctx.message_argument),
                trigger='cron',
                day_of_week=ctx.day,
                hour=ctx.hour,
                minute=ctx.minute,
                second=ctx.second,
                misfire_grace_time=10
            )

            save_alarms_to_file_in_json("channel", constants.CHANNEL_ALARMS)

            self.driver.direct_message(
                ctx.creator_id,
                "`%s` 알람이 `%s %s:%02d:%02d` 에 전달됩니다."
                % (ctx.name, ctx.day, ctx.hour, int(ctx.minute), int(ctx.second))
            )

    def is_alarm_already_scheduled(self, ctx: AlarmContext):
        job = constants.CHANNEL_ALARM_SCHEDULE.get_job(ctx.job_id)

        if job is not None:
            # 기존에 등록된 알람이 있는 경우, 기존 알람 정보 출력
            existing_ctx: AlarmContext = constants.CHANNEL_ALARMS[ctx.post_to][ctx.id]

            self.driver.direct_message(
                ctx.creator_id, "이미 등록된 알람이 있습니다. `%s알람예약취소` 후 재등록 해주세요.\n"
                                "**알람정보**\n"
                                "%s\n"
                                % (existing_ctx.name, existing_ctx.get_info()))
            return True
        else:
            return False

    def unschedule_alarm(self, alarm_name: str, alarm_id: str, message: Message, post_to: str):
        job_id = post_to + "_" + alarm_id
        job = constants.CHANNEL_ALARM_SCHEDULE.get_job(job_id)

        if job is not None:
            alarm_ctx: AlarmContext = constants.CHANNEL_ALARMS[post_to][alarm_id]

            self.driver.direct_message(
                alarm_ctx.creator_id,
                "등록하신 `%s` 알람이 %s님에 의해 삭제되었습니다.\n\n"
                "**알람정보**\n"
                "%s\n"
                % (alarm_ctx.name, message.sender_name, alarm_ctx.get_info())
            )

            del constants.CHANNEL_ALARMS[post_to][alarm_id]
            constants.CHANNEL_ALARM_SCHEDULE.remove_job(job_id)

            self.driver.direct_message(message.user_id, "`%s` 알람이 종료되었습니다." % alarm_name)

            save_alarms_to_file_in_json("channel", constants.CHANNEL_ALARMS)
        else:
            self.driver.direct_message(message.user_id, "등록된 알람이 없습니다.")
