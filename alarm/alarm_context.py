from common.utils import get_info_by_id


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

    interval: str
    interval_from: str

    message: str

    job_id: str
    job_status: str

    def __init__(
            self,
            creator_name: str, creator_id: str, post_to: str,
            name: str, id: str,
            day='', hour='00', minute='00', second='00',
            interval='', interval_from='',
            message='',
            job_status='실행'
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

        self.interval = interval
        self.interval_from = interval_from

        self.message = message

        self.job_id = post_to + "_" + id
        self.job_status = job_status

    def get_dict(self):
        return self.__dict__

    def get_info(self):
        message: str = ''
        message += f'   - 등록: @{self.creator_name}\n'

        if str(self.name).__len__() != 0:
            message += f'   - 알람: `{self.name}`\n'
        else:
            message += f'   - 알람: `{self.id}`\n'

        message += f'   - 대상: `{self.post_to}`'

        if self.post_to != self.creator_id:
            message += f'(`{get_info_by_id('channels', self.post_to)["display_name"]}`)'

        message += '\n'

        if self.interval == "":
            message += f'   - 주기: `{self.day} {self.hour}:{self.minute}:{self.second}`\n'
        else:
            message += f'   - 주기: `{self.interval}`\n'
            message += f'   - 기준: `{self.interval_from}`\n'

        if str(self.message).__len__() != 0:
            tmp = self.message.replace('\n', '\\n')
            message += f'   - 내용: `{tmp}`\n'

        message += f'   - 상태: `{self.job_status}` :{"recycle" if self.job_status == "실행" else "red_circle"}:'

        return message


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

    _interval: str
    _interval_from: str

    _message: str

    _job_status: str

    def __init__(self):
        self._name = ''

        self._day = ''
        self._hour = '00'
        self._minute = '00'
        self._second = '00'

        self._interval = ''
        self._interval_from = ''

        self._message = ''

        self._job_status = '실행'

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

    def interval(self, interval: str):
        self._interval = interval

        return self

    def interval_from(self, interval_from: str):
        self._interval_from = interval_from

        return self

    def message(self, message: str):
        self._message = message

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

            self._interval,
            self._interval_from,

            self._message,

            self._job_status
        )

        return alarm_context
