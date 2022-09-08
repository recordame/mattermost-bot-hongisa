from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

from commons.alarm import Alarm


class Plan(Plugin):
    plan_list: dict = {}
    plan = BackgroundScheduler()
    plan.start()
    plan.pause()

    @listen_to("^내규칙등록 ([a-zA-Z]+) (.+) (.+) (\*|[0-9]|[1-5][0-9]) (\*|[0-9]|[1-5][0-9]) (.+)$")
    def custom_alarm(self, message: Message, name: str, dow: str, h: str, m: str, s: str, txt: str):
        job_id = message.sender_name + "_" + name

        if self.plan.get_job(job_id) is not None:
            self.driver.direct_message(message.user_id, "동일한 이름의 규칙이 존재합니다. `내규칙목록`으로 확인해주세요")
        else:
            self.plan.add_job(
                id=job_id,
                func=lambda: self.driver.direct_message(message.user_id, txt),
                trigger='cron',
                day_of_week=dow,
                hour=h,
                minute=m,
                second=s
            )

            job = self.plan.get_job(job_id)
            alarm = Alarm(message.sender_name, message.user_id, job, dow, "%s:%s:%s" % (h, m, s), txt)

            self.driver.direct_message(message.user_id, "- 규칙이름: `%s`\n- 주기: `%s`\n- 시점: `%s:%s:%s`\n- 사용자 메시지: `%s`" % (name, dow, h, m, s, txt))

            if self.plan_list.get(message.sender_name) is not None:
                self.plan_list[message.sender_name].update({name: alarm})
            else:
                self.plan_list.update({message.sender_name: {name: alarm}})

        if self.plan.get_jobs().__len__() == 1:
            self.plan.resume()

    @listen_to("^내규칙목록$")
    def get_plan(self, message: Message):
        msg: str = ""

        if self.plan_list[message.sender_name] is not None:
            for alarm in self.plan_list[message.sender_name].values():
                msg += "[규칙]\n" + alarm.get_info() + "\n"

            self.driver.direct_message(message.user_id, "등록된 규칙 : %d 개\n" % (self.plan_list[message.sender_name].__len__()) + msg + "\n")
        else:
            self.driver.direct_message(message.user_id, "등록된 규칙 : 0 개")

    @listen_to("^내규칙삭제 (.+)$")
    def remove_plan(self, message: Message, name: str):
        self.plan.get_job(message.sender_name + "_" + name).remove()
        del self.plan_list[message.sender_name][name]

        self.driver.direct_message(message.user_id, "규칙`" + name + "`을 제거하였습니다.")

        if self.plan.get_jobs().__len__() == 0:
            self.plan.pause()
