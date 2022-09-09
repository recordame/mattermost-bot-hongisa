class Alarm:
    creator: str
    creator_id: str
    job_id: str
    interval: str
    time: str
    label: str
    txt: str

    def __init__(self, creator, creator_id, job_id, interval, time, label="", txt=""):
        self.creator = creator
        self.creator_id = creator_id
        self.job_id = job_id
        self.interval = interval
        self.time = time
        self.label = label
        self.txt = txt

    def get_info(self):
        msg = "   - 등록 : `%s`\n" % self.creator

        if len(self.label) != 0:
            msg += "   - 알림 : `%s`\n" % self.label
        else:
            msg += "   - 알림 : `%s`\n" % self.job_id

        msg += "   - 주기 : `%s %s`\n" % (self.interval, self.time)

        if len(self.txt) != 0:
            msg += "   - 내용 : `%s`" % self.txt

        return msg
