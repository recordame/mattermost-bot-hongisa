import logging
from abc import ABCMeta, abstractmethod

from mmpy_bot import Message
from mmpy_bot import Plugin

from alarm.alarm_context import AlarmContext
from alarm.alarm_util import save_alarms_to_file_in_json
from common import constant


class AbstractChannelAlarm(Plugin, metaclass=ABCMeta):
    @staticmethod
    def register_instance(name, _class: object):
        constant.BUILTIN_ALARM_INSTANCES.update({name: _class})

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
            msg = self.generate_message(args)

            if msg is not None:
                self.driver.create_post(post_to, self.generate_message(args))
                logging.info(f'{self.name}알람 전송 완료 - 목적지: {post_to}')
        except:
            logging.error(f'{self.name}알람 생성 중 에러 - 목적지: {post_to}')

    def schedule_alarm(self, ctx: AlarmContext, recovery_mode: bool = False, *args):
        if self.is_already_scheduled(ctx) is False:
            try:
                constant.CHANNEL_ALARM_SCHEDULER.add_job(
                    id=ctx.job_id,
                    func=lambda: self.alarm(ctx.post_to, args),
                    trigger='cron',
                    day_of_week=ctx.day,
                    hour=ctx.hour,
                    minute=ctx.minute,
                    second=ctx.second,
                    misfire_grace_time=60
                )

                ctx.job_status = '실행'
            except:
                self.driver.direct_message(ctx.creator_id, '인자 형식이 잘못되어 등록할 수 없었어요 :crying_cat_face:\n `도움말` `help` `?` 중 하나를 입력해 보세요.')
                return

            channel_alarms = constant.CHANNEL_ALARMS.get(ctx.post_to)

            if channel_alarms is not None:
                constant.CHANNEL_ALARMS[ctx.post_to].update({ctx.id: ctx})
            else:
                constant.CHANNEL_ALARMS.update({ctx.post_to: {ctx.id: ctx}})

            logging.info(f'[stat] 채널알람등록({ctx.name})')

            if not recovery_mode:
                save_alarms_to_file_in_json('채널', constant.CHANNEL_ALARMS)

                self.driver.direct_message(
                    ctx.creator_id,
                    f'`{ctx.name}` 을/를 `{ctx.day} {ctx.hour}:{ctx.minute}:{ctx.second}` 에 전달해드릴게요 :dizzy:'
                )

                self.advertise_web_interface(ctx.creator_id, ctx.creator_name)

    def is_already_scheduled(self, ctx: AlarmContext):
        job = constant.CHANNEL_ALARM_SCHEDULER.get_job(ctx.job_id)

        if job is not None:
            existing_ctx: AlarmContext = constant.CHANNEL_ALARMS[ctx.post_to][ctx.id]

            self.driver.direct_message(
                ctx.creator_id, f'이미 등록된 항목이 있어요! 취소 후 재등록해주세요.\n'
                                f'**항목 정보**\n'
                                f'{existing_ctx.get_info()}\n'
            )

            return True
        else:
            return False

    def unschedule_alarm(self, alarm_name: str, alarm_id: str, message: Message, post_to: str):
        job_id = post_to + "_" + alarm_id
        job = constant.CHANNEL_ALARM_SCHEDULER.get_job(job_id)

        if job is not None:
            alarm_ctx: AlarmContext = constant.CHANNEL_ALARMS[post_to][alarm_id]

            del constant.CHANNEL_ALARMS[post_to][alarm_id]
            constant.CHANNEL_ALARM_SCHEDULER.remove_job(job_id)

            save_alarms_to_file_in_json('채널', constant.CHANNEL_ALARMS)

            logging.info(f'[stat] 채널알람삭제({alarm_name})')

            if alarm_ctx.creator_name != message.sender_name:
                # 알람 삭제 요청자가 알람 등록자와 다른경우, 등록자에게 알림
                self.driver.direct_message(
                    alarm_ctx.creator_id,
                    f'등록하신 `{alarm_ctx.name}` 항목이 {message.sender_name}님에 의해 삭제되었어요 :skull_and_crossbones:\n\n'
                    f'**삭제 항목**\n'
                    f'{alarm_ctx.get_info()}\n'
                )

            self.driver.direct_message(message.user_id, f'`{alarm_name}` 항목이 삭제되었어요 :skull_and_crossbones:')
        else:
            self.driver.direct_message(message.user_id, '등록된 항목이 없어요 :crying_cat_face:')
