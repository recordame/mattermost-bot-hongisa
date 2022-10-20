from mmpy_bot import Message, Plugin, listen_to

from commons import constants
from commons.alarm_context import AlarmContextBuilder
from commons.utils import save_alarms_to_file_in_json


class UserAlarm(Plugin):
    @listen_to("^개인알람등록 (.+) (.+) (.+) (\\d+) (\\d+) (.+)$")
    def add_user_alarm(self, message: Message, alarm_id: str, day_of_week: str, hour: str, minute: str, second: str, alarm_message: str):
        job_id = message.user_id + "_" + alarm_id

        if constants.USER_ALARM_SCHEDULE.get_job(job_id) is not None:
            self.driver.direct_message(message.user_id, "동일한 알람이 존재합니다. `개인알람목록`으로 확인해주세요.")
        else:
            ctx = AlarmContextBuilder() \
                .creator_name(message.sender_name).creator_id(message.user_id).post_to(message.user_id) \
                .id(alarm_id) \
                .day(day_of_week).hour(hour).minute(minute).second(second) \
                .message(alarm_message) \
                .build()

            try:
                constants.USER_ALARM_SCHEDULE.add_job(
                    id=ctx.job_id,
                    func=lambda: self.driver.direct_message(ctx.post_to, ctx.message),
                    trigger="cron",
                    day_of_week=ctx.day,
                    hour=ctx.hour,
                    minute=ctx.minute,
                    second=ctx.second,
                    misfire_grace_time=10
                )
            except:
                self.driver.direct_message(ctx.creator_id, "인자가 잘못되어 등록할 수 없었어요 :crying_cat_face:")
                return

            user_alarms = constants.USER_ALARMS.get(ctx.post_to)

            if user_alarms is not None:
                constants.USER_ALARMS[ctx.post_to].update({ctx.id: ctx})
            else:
                constants.USER_ALARMS.update({ctx.post_to: {ctx.id: ctx}})

            save_alarms_to_file_in_json("user", constants.USER_ALARMS)

            self.driver.direct_message(
                ctx.creator_id,
                "`%s` 알람이 `%s %s:%02d:%02d` 에 전달됩니다."
                % (ctx.id, ctx.day, ctx.hour, int(ctx.minute), int(ctx.second))
            )

    @listen_to("^개인알람취소 (.+)$")
    def cancel_user_alarm(self, message: Message, alarm_id: str):
        job_id = message.user_id + "_" + alarm_id
        job = constants.USER_ALARM_SCHEDULE.get_job(job_id)

        if job is not None:
            del constants.USER_ALARMS[message.user_id][alarm_id]
            constants.USER_ALARM_SCHEDULE.remove_job(job_id)

            self.driver.direct_message(message.user_id, "`%s` 알람이 종료되었습니다." % alarm_id)

            save_alarms_to_file_in_json("user", constants.USER_ALARMS)
        else:
            self.driver.direct_message(message.user_id, "등록된 알람이 없습니다.")
