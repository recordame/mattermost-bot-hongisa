from apscheduler.job import Job


class Alarm:
    creator: str
    creator_id: str
    job_id: str
    class_name: str
    interval: str
    time: str
    job: Job
    txt: str

    def __init__(self, creator, creator_id, job: Job, interval, time, txt=""):
        self.creator = creator
        self.creator_id = creator_id
        self.job_id = job.id
        self.class_name = job.name
        self.job = job
        self.interval = interval
        self.time = time
        self.txt = txt

    def get_info(self):
        msg = "   - 등록인 : `%s`\n   - 식별값 : `%s`\n   - 유형 : `%s`\n   - 주기 : `%s %s`\n   - 사용자 메시지 : `%s`" % \
              (self.creator, self.job_id, self.class_name, self.interval, self.time, self.txt)

        return msg
