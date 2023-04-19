from mmpy_bot import Message, listen_to

from alarm.alarm_context import AlarmContextBuilder
from alarm.custom.abstract_custom_alarm import AbstractCustomAlarm
from common import constant


class ChannelAlarm(AbstractCustomAlarm):
    name = "채널"

    @listen_to(
        "^%s알람등록"
        "\\s([a-zA-Z\\d]+)"  # 채널 아이디 
        "\\s([가-힣a-zA-Z\\-_\\d]+)"  # 알람명
        "\\s([((last|1st|2nd|3rd|\\dth)\\s)|(sun|mon|tue|wed|thu|fri|sat|last|\\*)|\\d*|\\,|\\-]+)"  # 일
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 시
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 분
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 초
        "\\s(.+)$"  # 메시지
        % name
    )
    def add_alarm_cron(
            self,
            message: Message,
            channel_id: str,
            alarm_id: str,
            day_of_week: str,
            hour: str,
            minute: str,
            second: str,
            alarm_message: str,
            recovery_mode: bool = False,
            job_status: str = "실행"
    ):
        ctx = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(channel_id) \
            .id(alarm_id) \
            .day(day_of_week.strip(" ")).hour(hour).minute(minute).second(second) \
            .message(alarm_message) \
            .job_status(job_status) \
            .build()

        self.schedule_alarm(
            message,
            self.name,
            ctx,
            constant.CHANNEL_ALARMS,
            constant.CHANNEL_ALARM_SCHEDULER,
            recovery_mode
        )

    @listen_to(
        "^%s알람등록"
        "\\s([a-zA-Z\\d]+)"  # 채널 아이디 
        "\\s([가-힣a-zA-Z\\-_\\d]+)"  # 알람명
        "\\s(\\d*seconds|\\d*minutes|\\d*hours|\\d*days|\\d*weeks)"  # 주기
        "\\s(\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2})?)"  # 시작일
        "\\s(.+)$"  # 메시지
        % name
    )
    def add_alarm_interval(
            self,
            message: Message,
            channel_id: str,
            alarm_id: str,
            interval: str,
            interval_from: str,
            interval_time: str,
            alarm_message: str,
            recovery_mode: bool = False,
            job_status: str = "실행"
    ):
        ctx = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(channel_id) \
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
            constant.CHANNEL_ALARMS,
            constant.CHANNEL_ALARM_SCHEDULER,
            recovery_mode
        )

    @listen_to(
        "^%s알람취소"
        "\\s([a-zA-Z\\d]+)"  # 채널 ID
        "\\s([가-힣a-zA-Z\\-_\\d]+)$"  # 알람명
        % name
    )
    def cancel_alarm(self, message: Message, channel_id: str, alarm_id: str):
        self.unschedule_alarm(
            message,
            self.name,
            channel_id,
            alarm_id,
            constant.CHANNEL_ALARMS,
            constant.CHANNEL_ALARM_SCHEDULER
        )
