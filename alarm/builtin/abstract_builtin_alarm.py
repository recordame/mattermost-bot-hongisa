from abc import ABCMeta, abstractmethod

from mattermostdriver.exceptions import ResourceNotFound
from mmpy_bot import Message
from mmpy_bot import Plugin

from alarm.alarm_context import AlarmContext
from alarm.alarm_util import save_alarms_to_file_in_json
from common import constant


class AbstractBuiltinAlarm(Plugin, metaclass=ABCMeta):
    @staticmethod
    def add_builtin_alarm(name, _class: object):
        constant.BUILTIN_ALARM_INSTANCE.update({name: _class})

    @abstractmethod
    def generate_message(self, *args) -> str:
        pass

    @abstractmethod
    def add_alarm(self, message: Message, hour: str, minute: str):
        pass

    @abstractmethod
    def cancel_alarm(self, message: Message):
        pass

    def alarm(self, post_to: str, *args):
        try:
            self.driver.channels.get_channel(post_to)

            self.driver.create_post(post_to, self.generate_message(args))
        except ResourceNotFound:
            self.driver.direct_message(post_to, self.generate_message(args))

    def schedule_alarm(self, ctx: AlarmContext, recovery_mode: bool = False, *args):
        if self.is_alarm_already_scheduled(ctx) is False:
            try:
                constant.CHANNEL_ALARM_SCHEDULER.add_job(
                    id=ctx.job_id,
                    func=lambda: self.alarm(ctx.post_to, args),
                    trigger='cron',
                    day_of_week=ctx.day,
                    hour=ctx.hour,
                    minute=ctx.minute,
                    second=ctx.second,
                    misfire_grace_time=10
                )

                ctx.job_status = '실행'
            except:
                self.driver.direct_message(ctx.creator_id, '인자가 잘못되어 등록할 수 없었어요 :crying_cat_face:')

                return

            channel_alarms = constant.CHANNEL_ALARMS.get(ctx.post_to)

            if channel_alarms is not None:
                constant.CHANNEL_ALARMS[ctx.post_to].update({ctx.id: ctx})
            else:
                constant.CHANNEL_ALARMS.update({ctx.post_to: {ctx.id: ctx}})

            save_alarms()

            if not recovery_mode:
                self.driver.direct_message(
                    ctx.creator_id,
                    '`%s` 채널알람을 `%s %s:%02d:%02d`에 전달해드릴게요 :fairy:'
                    % (ctx.name, ctx.day, ctx.hour, int(ctx.minute), int(ctx.second))
                )

    def is_alarm_already_scheduled(self, ctx: AlarmContext) -> bool:
        job = constant.CHANNEL_ALARM_SCHEDULER.get_job(ctx.job_id)

        if job is not None:
            # 기존에 등록된 알람이 있는 경우, 기존 알람 정보 출력
            existing_ctx: AlarmContext = constant.CHANNEL_ALARMS[ctx.post_to][ctx.id]

            self.driver.direct_message(
                ctx.creator_id, '이미 등록된 채널알람이 있어요! `%s알람취소` 후 재등록해주세요.\n'
                                '**알람정보**\n'
                                '%s\n'
                                % (existing_ctx.name, existing_ctx.get_info()))
            return True
        else:
            return False

    def unschedule_alarm(self, alarm_name: str, alarm_id: str, message: Message, post_to: str):
        job_id = post_to + '_' + alarm_id
        job = constant.CHANNEL_ALARM_SCHEDULER.get_job(job_id)

        if job is not None:
            alarm_ctx: AlarmContext = constant.CHANNEL_ALARMS[post_to][alarm_id]

            self.driver.direct_message(
                alarm_ctx.creator_id,
                '등록하신 `%s` 채널알람이 %s님에 의해 삭제되었어요 :skull_and_crossbones:\n\n'
                '**알람정보**\n'
                '%s\n'
                % (alarm_ctx.name, message.sender_name, alarm_ctx.get_info())
            )

            del constant.CHANNEL_ALARMS[post_to][alarm_id]
            constant.CHANNEL_ALARM_SCHEDULER.remove_job(job_id)

            self.driver.direct_message(message.user_id, '`%s` 채널알람이 삭제되었어요 :skull_and_crossbones:' % alarm_name)

            save_alarms()
        else:
            self.driver.direct_message(message.user_id, '등록된 채널알람이 없어요 :crying_cat_face:')


###################

def save_alarms():
    save_alarms_to_file_in_json('channel', constant.CHANNEL_ALARMS)
