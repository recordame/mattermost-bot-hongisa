import re
from abc import ABCMeta, abstractmethod

from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Plugin, Message

from alarm.alarm_context import AlarmContext
from alarm.alarm_util import save_alarms_to_file_in_json
from common import constant


class AbstractCustomAlarm(Plugin, metaclass=ABCMeta):
    @abstractmethod
    def add_alarm(self):
        pass

    @abstractmethod
    def cancel_alarm(self):
        pass

    def schedule_alarm(
            self,
            message: Message,
            alarm_type: str,
            ctx: AlarmContext,
            alarm_contexts: dict,
            alarm_scheduler: BackgroundScheduler,
            recovery_mode: bool = False
    ):
        if alarm_scheduler.get_job(ctx.job_id) is not None:
            self.driver.direct_message(message.user_id, "이미 등록된 %s알람이 있어요! `%s알람취소` 후 재등록해주세요." % (alarm_type, alarm_type))
        else:
            message_function = self.get_message_function(alarm_type, ctx.message, ctx.post_to)

            try:
                alarm_job = self.create_alarm_job(ctx, alarm_scheduler, message_function)

                if ctx.job_status == "정지":
                    alarm_job.pause()
            except:
                self.driver.direct_message(ctx.creator_id, "인자가 잘못되어 등록할 수 없었어요 :crying_cat_face:")

                return

            alarms = alarm_contexts.get(ctx.post_to)

            if alarms is not None:
                alarm_contexts[ctx.post_to].update({ctx.id: ctx})
            else:
                alarm_contexts.update({ctx.post_to: {ctx.id: ctx}})

            save_alarms_to_file_in_json(alarm_type, alarm_contexts)

            if not recovery_mode:
                if ctx.interval == "":
                    self.driver.direct_message(
                        ctx.creator_id,
                        "`%s` %s알람을 `%s %s:%02d:%02d`에 전달해드릴게요 :dizzy:"
                        % (ctx.id, alarm_type, ctx.day, ctx.hour, int(ctx.minute), int(ctx.second))
                    )
                else:
                    self.driver.direct_message(
                        ctx.creator_id,
                        "`%s` %s알람을 `%s`부터 매 `%s` akek 전달해드릴게요 :dizzy:"
                        % (ctx.id, alarm_type, ctx.interval_from, ctx.interval)
                    )

    def suspend_alarm(
            self,
            message: Message,
            alarm_type: str,
            user_or_channel_id: str,
            alarm_id,
            alarm_contexts: dict,
            alarm_scheduler: BackgroundScheduler
    ):
        if alarm_id is None:
            try:
                alarms: dict = alarm_contexts[user_or_channel_id]
                dirty: bool = False

                for alarm in alarms.values():
                    if alarm.job_status == "실행":
                        dirty = True

                        alarm_scheduler.get_job(alarm.job_id).pause()
                        alarm.job_status = "정지"

                        self.send_alarm_status(message.user_id, alarm.id, alarm_type, "정지", "red_circle")

                if dirty:
                    save_alarms_to_file_in_json(alarm_type, alarm_contexts)
                else:
                    self.driver.direct_message(message.user_id, "모든 %s알람이 정지상태예요 :wink:" % alarm_type)

            except KeyError:
                self.driver.direct_message(message.user_id, "등록된 %s알람이 없어요 :crying_cat_face:" % alarm_type)

        else:
            job_id = user_or_channel_id + "_" + alarm_id
            job = alarm_scheduler.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, "등록된 %s알람이 없어요 :crying_cat_face:" % alarm_type)
            else:
                job.pause()

                ctx = alarm_contexts[user_or_channel_id][alarm_id]
                ctx.job_status = "정지"

                save_alarms_to_file_in_json(alarm_type, alarm_contexts)

                self.send_alarm_status(message.user_id, alarm_id, alarm_type, "정지", "red_circle")

    def continue_alarm(
            self,
            message: Message,
            alarm_type: str,
            user_or_channel_id: str,
            alarm_id,
            alarm_contexts: dict,
            alarm_scheduler: BackgroundScheduler
    ):
        if alarm_id is None:
            try:
                alarms: dict = alarm_contexts[user_or_channel_id]
                dirty: bool = False

                for alarm in alarms.values():
                    if alarm.job_status == "정지":
                        dirty = True

                        alarm_scheduler.get_job(alarm.job_id).resume()
                        alarm.job_status = "실행"

                        self.send_alarm_status(message.user_id, alarm.id, alarm_type, "재개", "recycle")

                if dirty:
                    save_alarms_to_file_in_json(alarm_type, alarm_contexts)
                else:
                    self.driver.direct_message(message.user_id, "모든 %s알람이 실행중이네요 :wink:" % alarm_type)

            except KeyError:
                self.driver.direct_message(message.user_id, "등록된 %s알람이 없어요 :crying_cat_face:" % alarm_type)

        else:
            job_id = user_or_channel_id + "_" + alarm_id
            job = alarm_scheduler.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, "등록된 %s알람이 없어요 :crying_cat_face:" % alarm_type)
            else:
                job.resume()

                ctx = alarm_contexts[user_or_channel_id][alarm_id]
                ctx.job_status = "실행"

                save_alarms_to_file_in_json(alarm_type, alarm_contexts)

                self.send_alarm_status(message.user_id, alarm_id, alarm_type, "재개", "recycle")

    def unschedule_alarm(
            self, message: Message,
            alarm_type: str,
            user_or_channel_id: str,
            alarm_id: str,
            alarm_contexts: dict,
            alarm_scheduler: BackgroundScheduler
    ):
        if alarm_id is None:
            try:
                alarms: dict = alarm_contexts[user_or_channel_id]

                for alarm in alarms.values():
                    del alarm_contexts[user_or_channel_id][alarm.id]
                    alarm_scheduler.remove_job(alarm.job_id)

                    save_alarms_to_file_in_json(alarm_type, alarm_contexts)

                    self.send_alarm_status(message.user_id, alarm.id, alarm_type, "삭제", "skull_and_crossbones")

            except KeyError:
                self.driver.direct_message(message.user_id, "등록된 %s알람이 없어요 :crying_cat_face:" % alarm_type)

        else:
            job_id = user_or_channel_id + "_" + alarm_id
            job = alarm_scheduler.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, "등록된 %s알람이 없어요 :crying_cat_face:" % alarm_type)
            else:
                del alarm_contexts[user_or_channel_id][alarm_id]
                alarm_scheduler.remove_job(job_id)

                save_alarms_to_file_in_json(alarm_type, alarm_contexts)

                self.send_alarm_status(message.user_id, alarm_id, alarm_type, "삭제", "skull_and_crossbones")

    def send_alarm_status(self, user_id: str, alarm_id: str, alarm_type: str, status: str, icon: str):
        self.driver.direct_message(user_id, "`%s` %s알람이 %s되었어요 :%s:" % (alarm_id, alarm_type, status, icon))

    def get_message_function(self, alarm_type: str, alarm_message: str, post_to: str):
        if "$미사" in alarm_message:
            before_insertion = alarm_message.split("$미사")[0].replace("\\n", "\n")
            after_insertion = alarm_message.split("$미사")[1].replace("\\n", "\n")

            if alarm_type == "채널":
                message_function = lambda: self.driver.create_post(
                    post_to,
                    before_insertion +
                    str(constant.BUILTIN_ALARM_INSTANCE.get("미사").generate_message()).removeprefix("@here").strip(" ") +
                    after_insertion
                )
            else:
                message_function = lambda: self.driver.direct_message(
                    post_to,
                    before_insertion +
                    str(constant.BUILTIN_ALARM_INSTANCE.get("미사").generate_message()).removeprefix("@here").strip(" ") +
                    after_insertion
                )
        else:
            if alarm_type == "채널":
                message_function = lambda: self.driver.create_post(
                    post_to,
                    alarm_message.replace("\\n", "\n")
                )
            else:
                message_function = lambda: self.driver.direct_message(
                    post_to,
                    alarm_message.replace("\\n", "\n")
                )

        return message_function

    def create_alarm_job(self, ctx: AlarmContext, alarm_scheduler: BackgroundScheduler, message_function) -> Job:
        if ctx.interval == "":
            if re.match("^(((1st|2nd|3rd|\\dth|last)\\s(sun|mon|tue|wed|thu|fri|sat))|last", ctx.day) \
                   or re.match("^\\d*(-\\d*)?", ctx.day) \
                   or re.match("^\\d*(,\\d*)?", ctx.day):
                alarm_job = alarm_scheduler.add_job(
                    id=ctx.job_id,
                    func=message_function,
                    trigger="cron",
                    day=ctx.day,
                    hour=ctx.hour,
                    minute=ctx.minute,
                    second=ctx.second,
                    misfire_grace_time=10
                )
            elif re.match("^(sun|mon|tue|wed|thu|fri|sat|\\*|,|-)+", ctx.day):
                alarm_job = alarm_scheduler.add_job(
                    id=ctx.job_id,
                    func=message_function,
                    trigger="cron",
                    day_of_week=ctx.day,
                    hour=ctx.hour,
                    minute=ctx.minute,
                    second=ctx.second,
                    misfire_grace_time=10
                )
        else:
            if re.match("^\\d*seconds", ctx.interval):
                alarm_job = alarm_scheduler.add_job(
                    id=ctx.job_id,
                    func=message_function,
                    trigger="interval",
                    seconds=int(ctx.interval.replace("seconds", "")),
                    start_date=ctx.interval_from,
                    misfire_grace_time=10
                )
            elif re.match("^\\d*minutes", ctx.interval):
                alarm_job = alarm_scheduler.add_job(
                    id=ctx.job_id,
                    func=message_function,
                    trigger="interval",
                    minutes=int(ctx.interval.replace("minutes", "")),
                    start_date=ctx.interval_from,
                    misfire_grace_time=10
                )
            elif re.match("^\\d*hours", ctx.interval):
                alarm_job = alarm_scheduler.add_job(
                    id=ctx.job_id,
                    func=message_function,
                    trigger="interval",
                    hours=int(ctx.interval.replace("minutes", "")),
                    start_date=ctx.interval_from,
                    misfire_grace_time=10
                )
            elif re.match("^\\d*days", ctx.interval):
                alarm_job = alarm_scheduler.add_job(
                    id=ctx.job_id,
                    func=message_function,
                    trigger="interval",
                    days=int(ctx.interval.replace("minutes", "")),
                    start_date=ctx.interval_from,
                    misfire_grace_time=10
                )
            elif re.match("^\\d*week", ctx.interval):
                alarm_job = alarm_scheduler.add_job(
                    id=ctx.job_id,
                    func=message_function,
                    trigger="interval",
                    week=int(ctx.interval.replace("minutes", "")),
                    start_date=ctx.interval_from,
                    misfire_grace_time=10
                )

        return alarm_job
