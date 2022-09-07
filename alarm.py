from apscheduler.job import Job


class Alarm:
    creator: str
    creater_id: str
    job_id: str
    class_name: str
    interval: str
    time: str
    job: Job

    def __init__(self, creator, creator_id, job: Job, interval, time):
        self.creator = creator
        self.creater_id = creator_id
        self.job_id = job.id
        self.class_name = job.name
        self.job = job
        self.interval = interval
        self.time = time

    def get_info(self):
        msg = "   - 등록인 : `%s`\n   - 식별값 : `%s`\n   - 유형 : `%s`\n   - 주기 : `%s %s`" % \
              (self.creator, self.job_id, self.class_name, self.interval, self.time)

        return msg
