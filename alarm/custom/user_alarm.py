import re

from mmpy_bot import Message, listen_to

from alarm.alarm_context import AlarmContextBuilder
from alarm.custom.abstract_custom_alarm import AbstractCustomAlarm
from common import constant


class UserAlarm(AbstractCustomAlarm):
    name = '개인'

    @listen_to(
        '^%s알람등록\\s'
        '([가-힣a-zA-Z\\-_\\d]+)\\s'  # 알람명
        '([((last|1st|2nd|3rd|\\dth)\\s)|(sun|mon|tue|wed|thu|fri|sat|last|\\*)|\\d|\\,|\\-]+)\\s'  # 일
        '([\\*|\\*/\\d|\\d{1,2}|\\-|\\,]+)\\s'  # 시
        '([\\*|\\*/\\d|\\d{1,2}|\\-|\\,]+)\\s'  # 분
        '([\\*|\\*/\\d|\\d{1,2}|\\-|\\,]+)\\s'  # 초
        '(.+)$'  # 메시지
        % name
    )
    def add_alarm(
            self,
            message: Message,
            alarm_id: str,
            day_of_week: str, hour: str, minute: str, second: str,
            alarm_message: str,
            job_status: str = '실행',
            recovery_mode: bool = False
    ):
        if (re.compile(f'^{self.pattern_dow}$').match(day_of_week) is not None) | \
                (re.compile(f'^{self.pattern_day}$').match(day_of_week) is not None) | \
                (re.compile(f'^{self.pattern_day_xth}$').match(day_of_week) is not None):
            ctx = AlarmContextBuilder() \
                .creator_name(message.sender_name).creator_id(message.user_id).post_to(message.user_id) \
                .name(self.name).id(alarm_id) \
                .day(day_of_week.strip(' ')).hour(hour).minute(minute).second(second) \
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
        else:
            self.driver.direct_message(message.user_id, "입력한 요일 형식에 문제가 있는것 같아요 :thinking-face:\n`도움말`을 확인해보세요!")

    @listen_to(
        '^%s알람등록\\s'
        '([가-힣a-zA-Z\\-_\\d]+)\\s'  # 알람명
        '(\\d+초|\\d+분|\\d+시간|\\d+일|\\d+주)\\s'  # 주기
        '(\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2})?)\\s'  # 시작일시
        '(.+)$'  # 메시지
        % name
    )
    def add_alarm_interval(
            self,
            message: Message,
            alarm_id: str,
            interval: str,
            interval_from: str,
            interval_time: str,  # 정규식 시작일중 시간영역을 위한 더미 변수
            alarm_message: str,
            job_status: str = '실행',
            recovery_mode: bool = False
    ):
        ctx = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(message.user_id) \
            .name(self.name).id(alarm_id) \
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
        '^%s알람정지'
        '\\s?([가-힣a-zA-Z\\-_\\d]+)?$'  # 알람명
        % name
    )
    def pause_alarm(self, message: Message, alarm_id: str = ''):
        self.suspend_alarm(
            message,
            self.name,
            message.user_id,
            alarm_id,
            constant.USER_ALARMS,
            constant.USER_ALARM_SCHEDULER
        )

    @listen_to(
        '^%s알람재개'
        '\\s?([가-힣a-zA-Z\\-_\\d]+)?$'  # 알람명
        % name
    )
    def resume_alarm(self, message: Message, alarm_id: str = ''):
        self.continue_alarm(
            message,
            self.name,
            message.user_id,
            alarm_id,
            constant.USER_ALARMS,
            constant.USER_ALARM_SCHEDULER
        )

    @listen_to(
        '^%s알람취소'
        '\\s?([가-힣a-zA-Z\\-_\\d]+)?$'  # 알람명
        % name
    )
    def cancel_alarm(self, message: Message, alarm_id: str = ''):
        self.unschedule_alarm(
            message,
            self.name,
            message.user_id,
            alarm_id,
            constant.USER_ALARMS,
            constant.USER_ALARM_SCHEDULER
        )
