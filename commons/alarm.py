class Alarm:
    creator: str
    job_id: str
    interval: str
    time: str
    msg: str

    def __init__(self, creator, job_id, interval, time, msg=""):
        self.creator = creator
        self.job_id = job_id
        self.interval = interval
        self.time = time
        self.msg = msg

    def get_info(self):
        msg = "   - 등록 : `%s`\n   - 알림 : `%s`\n   - 주기 : `%s %s`" % \
              (self.creator, self.job_id, self.interval, self.time)

        if len(self.msg) != 0:
            msg += "\n   - 내용 : `%s`" % self.msg

        return msg
