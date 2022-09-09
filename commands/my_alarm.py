from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

from commons import constant
from commons.alarm import Alarm


class MyAlarm(Plugin):

    @listen_to("^내알림등록 ([a-zA-Z]+) (.+) (.+) (\*|[0-9]|[1-5][0-9]) (\*|[0-9]|[1-5][0-9]) (.+)$")
    def add_my_alarm(self, message: Message, name: str, dow: str, h: str, m: str, s: str, txt: str):
        alarm_id = message.sender_name + "_" + name

        if constant.MY_SCHEDULE.get_job(alarm_id) is not None:
            self.driver.direct_message(message.user_id, "동일한 알림이 존재합니다. `내알림목록`으로 확인해주세요.")
        else:
            # 기존에 등록된 작업이 없는 경우, 새로운 알림 등록 및 시작
            constant.MY_SCHEDULE.add_job(
                id=alarm_id,
                func=lambda: self.driver.direct_message(message.user_id, txt),
                trigger='cron',
                day_of_week=dow,
                hour=h,
                minute=m,
                second=s
            )

            job = constant.MY_SCHEDULE.get_job(alarm_id)
            alarm = Alarm(message.sender_name, job.id, dow, "%s:%s:%s" % (h, m, s), txt)

            self.driver.direct_message(message.user_id,
                                       "- 등록: `%s`\n" % message.sender_name +
                                       "- 알림: `%s`\n" % name +
                                       "- 요일: `%s`\n" % dow +
                                       "- 패턴: `%s:%s:%s`\n" % (h, m, s) +
                                       "- 내용 : `%s`" % txt
                                       )

            my_alarms = constant.MY_ALARMS.get(message.sender_name)

            if my_alarms is not None:
                constant.MY_ALARMS[message.sender_name].update({name: alarm})
            else:
                constant.MY_ALARMS.update({message.sender_name: {name: alarm}})

    @listen_to("^내알림목록$")
    def get_my_alarm(self, message: Message):
        msg: str = ""

        my_alarms = constant.MY_ALARMS[message.sender_name]

        if my_alarms is not None:
            for alarm in my_alarms.values():
                msg += "[알림]\n" + alarm.get_info() + "\n"

            self.driver.direct_message(message.user_id, "등록된 알림 : %d 개\n" % (my_alarms.__len__()) + msg + "\n")
        else:
            self.driver.direct_message(message.user_id, "등록된 알림 : 0 개")

    @listen_to("^내알림취소 (.+)$")
    def cancel_my_alarm(self, message: Message, name: str):
        job_id = message.sender_name + "_" + name
        job = constant.MY_SCHEDULE.get_job(job_id)

        if job is not None:
            # 알림 리스트 및 백그라운드 스케쥴에서 제거
            del constant.MY_ALARMS[message.sender_name][name]
            constant.MY_SCHEDULE.get_job(job_id).remove()

            self.driver.direct_message(message.user_id, "`" + name + "` 알림이 종료되었습니다.")
        else:
            self.driver.direct_message(message.user_id, "등록된 알림이 없습니다.")
