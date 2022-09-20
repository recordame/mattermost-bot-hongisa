from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

from commons import constants
from commons.alarm_context import AlarmContext


class MyAlarm(Plugin):
    @listen_to("^내알림등록 ([a-zA-Z]+) (.+) (.+) (\*|[0-9]|[1-5][0-9]) (\*|[0-9]|[1-5][0-9]) (.+)$")
    def add_my_alarm(self, message: Message, label: str, dow: str, h: str, m: str, s: str, txt: str):
        alarm_id = message.sender_name + "_" + label

        if constants.MY_SCHEDULE.get_job(alarm_id) is not None:
            self.driver.direct_message(message.user_id, "동일한 알림이 존재합니다. `내알림목록`으로 확인해주세요.")
        else:
            # 기존에 등록된 작업이 없는 경우, 새로운 알림 등록 및 시작
            constants.MY_SCHEDULE.add_job(
                id=alarm_id,
                func=lambda: self.driver.direct_message(message.user_id, txt),
                trigger='cron',
                day_of_week=dow,
                hour=h,
                minute=m,
                second=s
            )

            job = constants.MY_SCHEDULE.get_job(alarm_id)
            alarm_ctx = AlarmContext(message.sender_name, message.user_id, job.id, dow, "%s:%s:%s" % (h, m, s), label, txt)

            self.driver.direct_message(message.user_id,
                                       "- 등록: `%s`\n" % message.sender_name +
                                       "- 알림: `%s`\n" % label +
                                       "- 요일: `%s`\n" % dow +
                                       "- 패턴: `%s:%s:%s`\n" % (h, m, s) +
                                       "- 내용 : `%s`" % txt
                                       )

            my_alarms = constants.MY_ALARMS.get(message.sender_name)

            if my_alarms is not None:
                constants.MY_ALARMS[message.sender_name].update({label: alarm_ctx})
            else:
                constants.MY_ALARMS.update({message.sender_name: {label: alarm_ctx}})

    @listen_to("^내알림목록$")
    def get_my_alarm(self, message: Message):
        msg: str = ""

        if constants.MY_ALARMS.get(message.sender_name) is not None:
            my_alarms = constants.MY_ALARMS[message.sender_name]

            for alarm in my_alarms.values():
                msg += "[알림]\n" + alarm.get_info() + "\n"

            self.driver.direct_message(message.user_id, "등록된 알림 : %d 개\n" % (my_alarms.__len__()) + msg + "\n")
        else:
            self.driver.direct_message(message.user_id, "등록된 알림 : 0 개")

    @listen_to("^내알림취소 (.+)$")
    def cancel_my_alarm(self, message: Message, label: str):
        job_id = message.sender_name + "_" + label
        job = constants.MY_SCHEDULE.get_job(job_id)

        if job is not None:
            # 알림 리스트 및 백그라운드 스케쥴에서 제거
            del constants.MY_ALARMS[message.sender_name][label]
            constants.MY_SCHEDULE.get_job(job_id).remove()

            self.driver.direct_message(message.user_id, "`" + label + "` 알림이 종료되었습니다.")
        else:
            self.driver.direct_message(message.user_id, "등록된 알림이 없습니다.")
