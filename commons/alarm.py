class Alarm:
    creator: str
    creator_id: str
    job_id: str
    interval: str
    time: str
    alarm_name: str
    alarm_text: str

    def __init__(self, creator: str, creator_id: str, job_id: str, interval: str, time: str, alarm_name: str = "", alarm_text: str = ""):
        self.creator = creator
        self.creator_id = creator_id
        self.job_id = job_id
        self.interval = interval
        self.time = time
        self.alarm_name = alarm_name
        self.alarm_text = alarm_text

    def get_info(self):
        msg = "   - 등록 : `%s`\n" % self.creator

        if str(self.alarm_name).__len__() != 0:
            msg += "   - 알림 : `%s`\n" % self.alarm_name
        else:
            msg += "   - 알림 : `%s`\n" % self.job_id

        msg += "   - 주기 : `%s %s`\n" % (self.interval, self.time)

        if str(self.alarm_text).__len__() != 0:
            msg += "   - 내용 : `%s`" % self.alarm_text

        return msg
