import re

from mmpy_bot import Message, Plugin, listen_to

from alarm.alarm_context import AlarmContextBuilder
from common import constant
from common.utils import save_alarms_to_file_in_json


class UserAlarm(Plugin):
    @listen_to(
        "^개인알람등록"
        "\\s([가-힣a-zA-Z\\-_\\d]+)"  # 알람명
        "\\s([(last\\s|\\dth\\s)?sun|mon|tue|wed|thu|fri|sat|,|\\-|\\d]+)"  # 일
        "\\s(\\*|\\d+)"  # 시
        "\\s(\\*|\\d+)"  # 분
        "\\s(\\*|\\d+)"  # 초
        "\\s(.+)$"  # 메시지
    )
    def add_user_alarm(self, message: Message, alarm_id: str, day_of_week: str, hour: str, minute: str, second: str, alarm_message: str, job_status: str = "실행"):
        job_id = message.user_id + "_" + alarm_id

        if constant.USER_ALARM_SCHEDULE.get_job(job_id) is not None:
            self.driver.direct_message(message.user_id, "이미 등록된 개인알람이 있어요! `개인알람취소` `%s` 후 재등록해주세요." % alarm_id)
        else:
            ctx = AlarmContextBuilder() \
                .creator_name(message.sender_name).creator_id(message.user_id).post_to(message.user_id) \
                .id(alarm_id) \
                .day(day_of_week.strip(" ")).hour(hour).minute(minute).second(second) \
                .message(alarm_message) \
                .build()

            regenerated_alarm_message: str = ""
            if "$치환변수" in alarm_message:
                regenerated_alarm_message += alarm_message.split("$치환변수")[0]
                regenerated_alarm_message += constant.BUILTIN_ALARM_INSTANCE.get("알람명").generate_message()
                regenerated_alarm_message += alarm_message.split("$치환변수")[1]
            else:
                regenerated_alarm_message = alarm_message

            regenerated_alarm_message = regenerated_alarm_message.replace("\\n", "\n")

            try:
                if re.match("^\\dth|last|\\d.+", ctx.day):
                    job = constant.USER_ALARM_SCHEDULE.add_job(
                        id=ctx.job_id,
                        func=lambda: self.driver.direct_message(ctx.post_to, regenerated_alarm_message),
                        trigger="cron",
                        day=ctx.day,
                        hour=ctx.hour,
                        minute=ctx.minute,
                        second=ctx.second,
                        misfire_grace_time=10
                    )
                else:
                    job = constant.USER_ALARM_SCHEDULE.add_job(
                        id=ctx.job_id,
                        func=lambda: self.driver.direct_message(ctx.post_to, regenerated_alarm_message),
                        trigger="cron",
                        day_of_week=ctx.day,
                        hour=ctx.hour,
                        minute=ctx.minute,
                        second=ctx.second,
                        misfire_grace_time=10
                    )

                ctx.job_status = job_status

                if job_status == "정지":
                    job.pause()
            except:
                self.driver.direct_message(ctx.creator_id, "인자가 잘못되어 등록할 수 없었어요 :crying_cat_face:")

                return

            user_alarms = constant.USER_ALARMS.get(ctx.post_to)

            if user_alarms is not None:
                constant.USER_ALARMS[ctx.post_to].update({ctx.id: ctx})
            else:
                constant.USER_ALARMS.update({ctx.post_to: {ctx.id: ctx}})

            save_alarms()

            self.driver.direct_message(
                ctx.creator_id,
                "`%s` 개인알람을 `%s %s:%02d:%02d`에 전달해드릴게요 :fairy:"
                % (ctx.id, ctx.day, ctx.hour, int(ctx.minute), int(ctx.second))
            )

    @listen_to(
        "^개인알람정지"
        "\\s?([가-힣a-zA-Z\\-_\\d]+)?$"  # 알람명
    )
    def pause_user_alarm(self, message: Message, alarm_id: str):
        if alarm_id is None:
            try:
                alarms: dict = constant.USER_ALARMS[message.user_id]
                dirty: bool = False

                for alarm in alarms.values():
                    if alarm.job_status == "실행":
                        dirty = True

                        constant.USER_ALARM_SCHEDULE.get_job(alarm.job_id).pause()
                        alarm.job_status = "정지"

                        self.send_alarm_status(message.user_id, alarm.id, "정지", "stop_sign")

                if dirty:
                    save_alarms()
                else:
                    self.driver.direct_message(message.user_id, "모든 개인알람이 정지상태예요 :wink:")

            except KeyError:
                self.driver.direct_message(message.user_id, "등록된 개인알람이 없어요 :crying_cat_face:")

        else:
            job_id = message.user_id + "_" + alarm_id
            job = constant.USER_ALARM_SCHEDULE.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, "등록된 개인알람이 없어요 :crying_cat_face:")
            else:
                job.pause()

                ctx = constant.USER_ALARMS[message.user_id][alarm_id]
                ctx.job_status = "정지"

                save_alarms()

                self.send_alarm_status(message.user_id, alarm_id, "정지", "stop_sign")

    @listen_to(
        "^개인알람재개"
        "\\s?([가-힣a-zA-Z\\-_\\d]+)?$"  # 알람명
    )
    def resume_user_alarm(self, message: Message, alarm_id: str):
        if alarm_id is None:
            try:
                alarms: dict = constant.USER_ALARMS[message.user_id]
                dirty: bool = False

                for alarm in alarms.values():
                    if alarm.job_status == "정지":
                        dirty = True

                        constant.USER_ALARM_SCHEDULE.get_job(alarm.job_id).resume()
                        alarm.job_status = "실행"

                        self.send_alarm_status(message.user_id, alarm.id, "재개", "large_green_circle")

                if dirty:
                    save_alarms()
                else:
                    self.driver.direct_message(message.user_id, "모든 개인알람이 실행중이네요 :wink:")

            except KeyError:
                self.driver.direct_message(message.user_id, "등록된 개인알람이 없어요 :crying_cat_face:")

        else:
            job_id = message.user_id + "_" + alarm_id
            job = constant.USER_ALARM_SCHEDULE.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, "등록된 개인알람이 없어요 :crying_cat_face:")
            else:
                job.resume()

                ctx = constant.USER_ALARMS[message.user_id][alarm_id]
                ctx.job_status = "실행"

                save_alarms()

                self.send_alarm_status(message.user_id, alarm_id, "재개", "large_green_circle")

    @listen_to(
        "^개인알람취소"
        "\\s?([가-힣a-zA-Z\\-_\\d]+)?$"  # 알람명
    )
    def cancel_user_alarm(self, message: Message, alarm_id: str):
        if alarm_id is None:
            try:
                alarms: dict = constant.USER_ALARMS[message.user_id]

                for alarm in alarms.values():
                    del constant.USER_ALARMS[message.user_id][alarm.id]
                    constant.USER_ALARM_SCHEDULE.remove_job(alarm.job_id)

                    save_alarms()

                    self.send_alarm_status(message.user_id, alarm.id, "삭제", "skull_and_crossbones")

            except KeyError:
                self.driver.direct_message(message.user_id, "등록된 개인알람이 없어요 :crying_cat_face:")

        else:
            job_id = message.user_id + "_" + alarm_id
            job = constant.USER_ALARM_SCHEDULE.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, "등록된 개인알람이 없어요 :crying_cat_face:")
            else:
                del constant.USER_ALARMS[message.user_id][alarm_id]
                constant.USER_ALARM_SCHEDULE.remove_job(job_id)

                save_alarms()

                self.send_alarm_status(message.user_id, alarm_id, "삭제", "skull_and_crossbones")

    def send_alarm_status(self, user_id: str, alarm_id: str, status: str, icon: str):
        self.driver.direct_message(user_id, "`%s` 개인알람이 %s되었어요 :%s: " % (alarm_id, status, icon))


###################

def save_alarms():
    save_alarms_to_file_in_json("user", constant.USER_ALARMS)
