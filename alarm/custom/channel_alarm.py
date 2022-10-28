import re

from mmpy_bot import Message, Plugin, listen_to

from alarm.alarm_context import AlarmContextBuilder
from alarm.alarm_util import save_alarms_to_file_in_json
from common import constant


class ChannelAlarm(Plugin):
    @listen_to(
        "^채널알람등록"
        "\\s([a-zA-Z\\d]+)"  # 채널 아이디 
        "\\s([가-힣a-zA-Z\\-_\\d]+)"  # 알람명
        "\\s([last|last\\s|\\dth\\s|sun|mon|tue|wed|thu|fri|sat|\\,|\\-|\\d|\\*]+)"  # 일
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 시
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 분
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"  # 초
        "\\s(.+)$"  # 메시지
    )
    def add_channel_alarm(
            self, message: Message,
            channel_id: str,
            alarm_id: str,
            day_of_week: str, hour: str, minute: str, second: str,
            alarm_message: str,
            recovery_mode: bool = False,
            job_status: str = "실행"
    ):
        job_id = channel_id + "_" + alarm_id

        if constant.CHANNEL_ALARM_SCHEDULE.get_job(job_id) is not None:
            self.driver.direct_message(message.user_id, "이미 등록된 채널알람이 있어요! `채널알람취소` `채널ID` `%s` 후 재등록해주세요." % alarm_id)
        else:
            ctx = AlarmContextBuilder() \
                .creator_name(message.sender_name).creator_id(message.user_id).post_to(channel_id) \
                .id(alarm_id) \
                .day(day_of_week.strip(" ")).hour(hour).minute(minute).second(second) \
                .message(alarm_message) \
                .build()

            message_function = lambda: self.driver.create_post(
                ctx.post_to,
                alarm_message.replace("\\n", "\n")
            )

            try:
                if re.match("^\\dth\\s|last|\\d.+", ctx.day):
                    constant.CHANNEL_ALARM_SCHEDULE.add_job(
                        id=ctx.job_id,
                        func=message_function,
                        trigger="cron",
                        day=ctx.day,
                        hour=ctx.hour,
                        minute=ctx.minute,
                        second=ctx.second,
                        misfire_grace_time=10
                    )
                else:
                    constant.CHANNEL_ALARM_SCHEDULE.add_job(
                        id=ctx.job_id,
                        func=message_function,
                        trigger="cron",
                        day_of_week=ctx.day,
                        hour=ctx.hour,
                        minute=ctx.minute,
                        second=ctx.second,
                        misfire_grace_time=10
                    )

                ctx.job_status = job_status
            except:
                self.driver.direct_message(ctx.creator_id, "인자가 잘못되어 등록할 수 없었어요 :crying_cat_face:")

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
                    "`%s` 개인알람을 `%s %s:%02d:%02d`에 전달해드릴게요 :fairy:"
                    % (ctx.id, ctx.day, ctx.hour, int(ctx.minute), int(ctx.second))
                )


@listen_to(
    "^채널알람취소"
    "\\s([a-zA-Z\\d]+)"  # 채널 ID
    "\\s([가-힣a-zA-Z\\-_\\d]+)$"  # 알람명
)
def cancel_channel_alarm(self, message: Message, channel_id: str, alarm_id: str):
    if alarm_id is None:
        try:
            alarms: dict = constant.CHANNEL_ALARMS[channel_id]

            for alarm in alarms.values():
                del constant.CHANNEL_ALARMS[channel_id][alarm.id]
                constant.CHANNEL_ALARM_SCHEDULE.remove_job(alarm.job_id)

                save_alarms()

                self.send_alarm_status(message.user_id, alarm.id, "삭제", "skull_and_crossbones")

        except KeyError:
            self.driver.direct_message(message.user_id, "등록된 채널알람이 없어요 :crying_cat_face:")

    else:
        job_id = channel_id + "_" + alarm_id
        job = constant.CHANNEL_ALARM_SCHEDULE.get_job(job_id)

        if job is None:
            self.driver.direct_message(message.user_id, "등록된 채널알람이 없어요 :crying_cat_face:")
        else:
            del constant.CHANNEL_ALARMS[channel_id][alarm_id]
            constant.CHANNEL_ALARM_SCHEDULE.remove_job(job_id)

            save_alarms()

            self.send_alarm_status(message.user_id, alarm_id, "삭제", "skull_and_crossbones")


def send_alarm_status(self, user_id: str, alarm_id: str, status: str, icon: str):
    self.driver.direct_message(user_id, "`%s` 채널알람이 %s되었어요 :%s: " % (alarm_id, status, icon))


###################

def save_alarms():
    save_alarms_to_file_in_json("channel", constant.CHANNEL_ALARMS)
