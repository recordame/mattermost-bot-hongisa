from mmpy_bot import Message, Plugin, listen_to

from commons import constants
from commons.alarm_context import AlarmContext
from commons.utils import save_personal_alarms_to_file_in_json


class MyAlarm(Plugin):
    @listen_to("^내알람등록 (.+) (.+) (.+) (\*|[0-9]|[1-5][0-9]) (\*|[0-9]|[1-5][0-9]) (.+)$")
    def add_my_alarm(self, message: Message, label: str, dow: str, hour: str, minute: str, second: str, msg: str):
        alarm_id = message.sender_name + "_" + label

        if constants.MY_SCHEDULE.get_job(alarm_id) is not None:
            self.driver.direct_message(message.user_id,
                                       "동일한 알람이 존재합니다. `내알람목록`으로 확인해주세요.")
        else:
            # 기존에 등록된 작업이 없는 경우, 새로운 알람 등록 및 시작
            constants.MY_SCHEDULE.add_job(
                id=alarm_id,
                func=lambda: self.driver.direct_message(message.user_id, msg),
                trigger="cron",
                day_of_week=dow,
                hour=hour,
                minute=minute,
                second=second,
                misfire_grace_time=10
            )

            job = constants.MY_SCHEDULE.get_job(alarm_id)
            alarm_ctx = AlarmContext(
                message.sender_name,
                message.user_id,
                job.id,
                dow,
                "%s:%s:%s" % (hour, minute, second),
                label,
                msg
            )

            self.driver.direct_message(
                message.user_id,
                "- 등록: `%s`\n" % message.sender_name
                + "- 알람: `%s`\n" % label
                + "- 요일: `%s`\n" % dow
                + "- 패턴: `%s:%s:%s`\n" % (hour, minute, second)
                + "- 내용 : `%s`" % msg,
            )

            my_alarms = constants.MY_ALARMS.get(message.sender_name)

            if my_alarms is not None:
                constants.MY_ALARMS[message.sender_name].update({label: alarm_ctx})
            else:
                constants.MY_ALARMS.update({message.sender_name: {label: alarm_ctx}})

            save_personal_alarms_to_file_in_json()

    @listen_to("^내알람목록$")
    def get_my_alarm(self, message: Message):
        msg: str = ""

        if constants.MY_ALARMS.get(message.sender_name) is not None:
            my_alarms = constants.MY_ALARMS[message.sender_name]

            for alarm in my_alarms.values():
                msg += "[알람]\n" + alarm.get_info() + "\n"

            self.driver.direct_message(
                message.user_id, "등록된 알람 : %d 개\n" % (my_alarms.__len__()) + msg + "\n"
            )
        else:
            self.driver.direct_message(message.user_id, "등록된 알람 : 0 개")

    @listen_to("^내알람취소 (.+)$")
    def cancel_my_alarm(self, message: Message, label: str):
        job_id = message.sender_name + "_" + label
        job = constants.MY_SCHEDULE.get_job(job_id)

        if job is not None:
            # 알람 리스트 및 백그라운드 스케쥴에서 제거
            del constants.MY_ALARMS[message.sender_name][label]
            constants.MY_SCHEDULE.get_job(job_id).remove()

            self.driver.direct_message(message.user_id, "`" + label + "` 알람이 종료되었습니다.")

            save_personal_alarms_to_file_in_json()
        else:
            self.driver.direct_message(message.user_id, "등록된 알람이 없습니다.")
