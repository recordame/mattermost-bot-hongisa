from apscheduler.events import EVENT_JOB_EXECUTED
from mmpy_bot import Message, listen_to

from alarm.alarm_context import AlarmContextBuilder
from alarm.alarm_util import save_alarms_to_file_in_json
from alarm.custom.abstract_custom_alarm import AbstractCustomAlarm
from common import constant


def listen_ephemeral_alarm_event(event):
    # 예약 메시지 작업이 실행된 후 알람 저장용 파일에서 삭제
    post_to = event.job_id.split('_')[0]
    alarm_id = event.job_id.split('_')[1]

    try:
        constant.EPHEMERAL_ALARMS.get(post_to).pop(alarm_id)

        if constant.EPHEMERAL_ALARMS.get(post_to).__len__() == 0:
            constant.EPHEMERAL_ALARMS.pop(post_to)

        save_alarms_to_file_in_json('예약', constant.EPHEMERAL_ALARMS)
    except:
        pass


constant.EPHEMERAL_ALARM_SCHEDULER.add_listener(listen_ephemeral_alarm_event, EVENT_JOB_EXECUTED)


#########################

class EphemeralAlarm(AbstractCustomAlarm):
    name = '예약'

    @listen_to(
        '^메시지%s\\s'
        '([a-zA-Z\\d]+)\\s'  # 메시지 목적지
        '([가-힣a-zA-Z\\-_\\d]+)\\s'  # 알람명
        '(\\d{4})\\s'  # yyyy
        '(\\d{1,2})\\s'  # MM
        '(\\d{1,2})\\s'  # dd
        '(\\d{1,2})\\s'  # hh
        '(\\d{1,2})\\s'  # mm
        '(\\d{1,2})\\s'  # ss
        '(.+)$'  # 메시지
        % name
    )
    def add_alarm(
            self,
            message: Message,
            post_to: str,
            alarm_id: str,
            year: str,
            month: str,
            day: str,
            hour: str,
            minute: str,
            second: str,
            alarm_message: str,
            job_status: str = '실행',
            recovery_mode: bool = False
    ):
        # 채널 예약 메시지 등록
        ctx = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(post_to) \
            .name(self.name).id(alarm_id) \
            .day(year + month.zfill(2) + day.zfill(2)).hour(hour.zfill(2)).minute(minute.zfill(2)).second(second.zfill(2)) \
            .message(alarm_message) \
            .job_status(job_status) \
            .build()

        self.schedule_alarm(
            message,
            self.name,
            ctx,
            constant.EPHEMERAL_ALARMS,
            constant.EPHEMERAL_ALARM_SCHEDULER,
            recovery_mode
        )

    @listen_to(
        '^메시지%s\\s'
        '([가-힣a-zA-Z\\-_\\d]+)\\s'  # 알람명
        '(\\d{4})\\s'  # yyyy
        '(\\d{1,2})\\s'  # MM
        '(\\d{1,2})\\s'  # dd
        '(\\d{1,2})\\s'  # hh
        '(\\d{1,2})\\s'  # mm
        '(\\d{1,2})\\s'  # ss
        '(.+)$'  # 메시지
        % name
    )
    def add_user_alarm(
            self,
            message: Message,
            alarm_id: str,
            year: str,
            month: str,
            day: str,
            hour: str,
            minute: str,
            second: str,
            alarm_message: str,
            job_status: str = '실행',
            recovery_mode: bool = False
    ):
        # 개인 예약 메시지 등록
        ctx = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(message.user_id) \
            .id(alarm_id) \
            .day(year + month.zfill(2) + day.zfill(2)).hour(hour.zfill(2)).minute(minute.zfill(2)).second(second.zfill(2)) \
            .message(alarm_message) \
            .job_status(job_status) \
            .build()

        self.schedule_alarm(
            message,
            self.name,
            ctx,
            constant.EPHEMERAL_ALARMS,
            constant.EPHEMERAL_ALARM_SCHEDULER,
            recovery_mode
        )

    @listen_to(
        '^메시지%s취소'
        '\\s([a-zA-Z\\d]+)'  # 메시지 목적지
        '\\s([가-힣a-zA-Z\\-_\\d]+)$'  # 알람명
        % name
    )
    def cancel_alarm(self, message: Message, post_to: str, alarm_id: str):
        # 채널 예약 메시지 취소
        self.unschedule_alarm(
            message,
            self.name,
            post_to,
            alarm_id,
            constant.EPHEMERAL_ALARMS,
            constant.EPHEMERAL_ALARM_SCHEDULER
        )

    @listen_to(
        '^메시지%s취소'
        '\\s([가-힣a-zA-Z\\-_\\d]+)$'  # 알람명
        % name
    )
    def cancel_user_alarm(self, message: Message, alarm_id: str):
        # 개인 예약 메시지 취소
        self.unschedule_alarm(
            message,
            self.name,
            message.user_id,
            alarm_id,
            constant.EPHEMERAL_ALARMS,
            constant.EPHEMERAL_ALARM_SCHEDULER
        )
