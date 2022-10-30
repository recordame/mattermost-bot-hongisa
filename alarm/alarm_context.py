class AlarmContext:
    creator_name: str
    creator_id: str
    post_to: str

    name: str
    id: str

    day: str
    hour: str
    minute: str
    second: str

    message: str
    message_argument: str

    job_id: str
    job_status: str

    def __init__(
            self,
            creator_name: str, creator_id: str, post_to: str,
            name: str, id: str,
            day: str, hour: str, minute="00", second="00",
            message="", message_argument="",
            job_status="실행"
    ):
        self.creator_name = creator_name
        self.creator_id = creator_id
        self.post_to = post_to

        self.name = name
        self.id = id

        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

        self.message = message
        self.message_argument = message_argument

        self.job_id = post_to + "_" + id
        self.job_status = job_status

    def get_info(self):
        msg: str = ""
        msg += "   - 등록 : `%s`\n" % self.creator_name

        if str(self.name).__len__() != 0:
            msg += "   - 알람 : `%s`\n" % self.name
        else:
            msg += "   - 알람 : `%s`\n" % self.id

        msg += "   - 대상 : `%s`\n" % self.post_to
        msg += "   - 주기 : `%s %s:%s:%s`\n" % (self.day, self.hour, self.minute, self.second)

        if str(self.message).__len__() != 0:
            msg += "   - 내용 : %s\n" % self.message

        msg += "   - 상태 : `%s` :%s:" % (self.job_status, "recycle" if self.job_status == "실행" else "red_circle")

        return msg


class AlarmContextBuilder:
    _creator_name: str
    _creator_id: str
    _post_to: str

    _name: str
    _id: str

    _day: str
    _hour: str
    _minute: str
    _second: str

    _message: str
    _message_argument: str

    _job_status: str

    def __init__(self):
        self._name = ""

        self._minute = "00"
        self._second = "00"

        self._message = ""
        self._message_argument = ""

    def creator_name(self, creator_name: str):
        self._creator_name = creator_name

        return self

    def creator_id(self, creator_id: str):
        self._creator_id = creator_id

        return self

    def name(self, name: str):
        self._name = name

        return self

    def id(self, id: str):
        self._id = id

        return self

    def post_to(self, post_to: str):
        self._post_to = post_to

        return self

    def day(self, day: str):
        self._day = day

        return self

    def hour(self, hour: str):
        self._hour = hour

        return self

    def minute(self, minute: str):
        self._minute = minute

        return self

    def second(self, second: str):
        self._second = second

        return self

    def message(self, message: str):
        self._message = message

        return self

    def message_argument(self, message_argument: str):
        self._message_argument = message_argument

        return self

    def job_status(self, job_status: str):
        self._job_status = job_status

        return self

    def build(self):
        alarm_context: AlarmContext = AlarmContext(
            self._creator_name,
            self._creator_id,
            self._post_to,

            self._name,
            self._id,

            self._day,
            self._hour,
            self._minute,
            self._second,

            self._message,
            self._message_argument
        )

        return alarm_context
