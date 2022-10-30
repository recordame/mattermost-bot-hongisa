from urllib.request import urlopen, Request

import bs4
import urllib3
from mmpy_bot import Message
from mmpy_bot import listen_to

from alarm.alarm_context import AlarmContextBuilder
from alarm.builtin.abstract_builtin_alarm import AbstractBuiltinAlarm
from common import constant

urllib3.disable_warnings()


class MassAlarm(AbstractBuiltinAlarm):
    name = "미사"
    id = "mass"
    day = "sun"
    channel_id = constant.CH_NOTIFICATIONS_ID

    def __init__(self):
        super().__init__()
        self.add_builtin_alarm(self.name, self)

    def generate_message(self, option: str = ""):
        web_page = load_web_page()
        mass_information = extract_mass_information(web_page)

        msg = "@here " + mass_information + "\n" \
              + "평화를 빕니다 :pray:\n" \
              + "https://aos.catholic.or.kr/pro1021/everydayMass"

        return msg

    @listen_to("^%s$" % name)
    def direct(self, message: Message):
        self.alarm(message.user_id)

    @listen_to("^%s알림$" % name)
    def notify(self, message: Message, post_to=channel_id):
        self.alarm(post_to)

    @listen_to(
        "^%s알람등록"
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)"
        "\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)$"
        % name
    )
    def add_alarm(self, message: Message, hour: str, minute: str, recovery_mode: bool = False):
        alarm_context = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(self.channel_id) \
            .name(self.name).id(self.id) \
            .day(self.day).hour(hour).minute(minute) \
            .build()

        self.schedule_alarm(alarm_context, recovery_mode)

    @listen_to("^%s알람취소$" % name)
    def cancel_alarm(self, message: Message, post_to=channel_id):
        self.unschedule_alarm(self.name, self.id, message, post_to)


##########################

def load_web_page():
    # 서울대교구
    url: str = "https://aos.catholic.or.kr/pro1021/everydayMass"

    req = Request(url)
    page = urlopen(req)
    html = page.read().decode('utf-8')
    soup = bs4.BeautifulSoup(html, "html.parser")

    return soup


def extract_mass_information(info: str):
    today = info.find('p', class_="bibleBox").text.replace("  ", " ")
    mass_day = info.find('em').text
    mass_title = info.find('p', class_="bibleTit").text;

    msg = "`" + today + "`" + "\n**" + mass_day + "**\n >" + mass_title + "\n"

    return msg
