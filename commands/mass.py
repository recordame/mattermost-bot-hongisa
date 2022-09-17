from urllib.request import urlopen, Request

import bs4
import urllib3
from mmpy_bot import Message
from mmpy_bot import listen_to

from commons import constant
from commons.abstract_alarm import AbstractAlarm

urllib3.disable_warnings()


# 서울대교구 매일미사 페이지 로드
def get_info():
    # 서울대교구
    url: str = "https://aos.catholic.or.kr/pro1021/everydayMass"

    req = Request(url)
    page = urlopen(req)
    html = page.read().decode('utf-8')
    soup = bs4.BeautifulSoup(html, "html.parser")

    return soup


# 매일미사 정보 추출
def extract_mass(info: str):
    today = info.find('p', class_="bibleBox").text.replace("  ", " ")
    mass_day = info.find('em').text
    mass_title = info.find('p', class_="bibleTit").text;

    msg = "`" + today + "`" + "\n**" + mass_day + "**\n >" + mass_title + "\n"

    return msg


class MassAlarm(AbstractAlarm):
    name = "미사"

    def __init__(self):
        self.id = "MassAlarm"
        self.day = "sun"
        self.ch = constant.CH_NOTIFICATIONS_ID
        self.msg = self.generate_msg()

    def generate_msg(self):
        info = get_info()
        mass = extract_mass(info)

        msg = "@here " + mass + "\n" \
              + "평화를 빕니다 :pray:\n" \
              + "https://aos.catholic.or.kr/pro1021/everydayMass"

        return msg

    @listen_to("^%s$" % name)
    def direct(self, message: Message):
        self.alarm(message.user_id, False)

    @listen_to("^%s알림$" % name)
    def notify(self, message: Message):
        self.alarm(self.ch)

    @listen_to("^%s알림예약 (.+) (.+)$" % name)
    def add_alarm(self, message: Message, hour: str, minute: str):
        self.schedule_alarm(message, hour, minute)

    @listen_to("^%s알림예약취소$" % name)
    def cancel_alarm(self, message: Message):
        self.unschedule_alarm(self.name, message)
