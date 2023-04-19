from mmpy_bot import Message, listen_to

from alarm.alarm_context import AlarmContextBuilder
from alarm.custom.abstract_custom_alarm import AbstractCustomAlarm
from common import constant


class UserAlarm(AbstractCustomAlarm):
    name = "개인"

    @listen_to(
        "^%s알람등록"
        "\\s([가-힣a-zA-Z\\-_\\d]+)"  # 알람명
        "\\s([last|last\\s|1st\\s|2nd\\s|3rd\\s|\\dth\\s|sun|mon|tue|wed|thu|fri|sat|\\,|\\-|\\d|\\*]+)"  # 일
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 시
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 분
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 초
        "\\s(.+)$"  # 메시지
        % name
    )
    def add_alarm(
            self, message: Message,
            alarm_id: str,
            day_of_week: str, hour: str, minute: str, second: str,
            alarm_message: str,
            recovery_mode: bool = False,
            job_status: str = "실행"
    ):
        ctx = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(message.user_id) \
            .id(alarm_id) \
            .day(day_of_week.strip(" ")).hour(hour).minute(minute).second(second) \
            .message(alarm_message) \
            .job_status(job_status) \
            .build()

        self.schedule_alarm(
            message,
            self.name,
            ctx,
            constant.USER_ALARMS,
            constant.USER_ALARM_SCHEDULER,
            recovery_mode
        )

    @listen_to(
        "^%s알람등록"
        "\\s([가-힣a-zA-Z\\-_\\d]+)"  # 알람명
        "\\s(\\d*seconds|\\d*minutes|\\d*hours|\\d*days|\\d*weeks)"  # 주기
        "\\s(\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2})?)"  # 시작일
        "\\s(.+)$"  # 메시지
        % name
    )
    def add_alarm_interval(
            self, message: Message,
            alarm_id: str,
            interval: str,
            interval_from: str,
            interval_time: str,
            alarm_message: str,
            recovery_mode: bool = False,
            job_status: str = "실행"
    ):
        ctx = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(message.user_id) \
            .id(alarm_id) \
            .interval(interval) \
            .interval_from(interval_from) \
            .message(alarm_message) \
            .job_status(job_status) \
            .build()

        self.schedule_alarm(
            message,
            self.name,
            ctx,
            constant.USER_ALARMS,
            constant.USER_ALARM_SCHEDULER,
            recovery_mode
        )
        
    @listen_to(
        "^%s알람정지"
        "\\s?([가-힣a-zA-Z\\-_\\d]+)?$"  # 알람명
        % name
    )
    def pause_alarm(self, message: Message, alarm_id: str):
        self.suspend_alarm(
            message,
            self.name,
            message.user_id,
            alarm_id,
            constant.USER_ALARMS,
            constant.USER_ALARM_SCHEDULER
        )

    @listen_to(
        "^%s알람재개"
        "\\s?([가-힣a-zA-Z\\-_\\d]+)?$"  # 알람명
        % name
    )
    def resume_alarm(self, message: Message, alarm_id: str):
        self.continue_alarm(
            message,
            self.name,
            message.user_id,
            alarm_id,
            constant.USER_ALARMS,
            constant.USER_ALARM_SCHEDULER
        )

    @listen_to(
        "^%s알람취소"
        "\\s?([가-힣a-zA-Z\\-_\\d]+)?$"  # 알람명
        % name
    )
    def cancel_alarm(self, message: Message, alarm_id: str):
        self.unschedule_alarm(
            message,
            self.name,
            message.user_id,
            alarm_id,
            constant.USER_ALARMS,
            constant.USER_ALARM_SCHEDULER
        )
