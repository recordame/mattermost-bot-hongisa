from urllib.request import urlopen, Request

import bs4
import urllib3
from mmpy_bot import Message
from mmpy_bot import listen_to

from commons import constants
from commons.alarm import Alarm
from commons.alarm_context import AlarmContextBuilder

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


class MassAlarm(Alarm):
    name = "미사"
    id = "MassAlarm"
    day = "sun"
    ch = constants.CH_NOTIFICATIONS_ID

    def generate_msg(self, option: str = ""):
        info = get_info()
        mass = extract_mass(info)

        msg = "@here " + mass + "\n" \
              + "평화를 빕니다 :pray:\n" \
              + "https://aos.catholic.or.kr/pro1021/everydayMass"

        return msg

    @listen_to("^%s$" % name)
    def direct(self, message: Message):
        self.alarm("to_channel", message.user_id)

    @listen_to("^%s알람$" % name)
    def notify(self, message: Message, post_to=ch):
        self.alarm("to_channel", post_to)

    @listen_to("^%s알람예약 (.+) (\\d+)$" % name)
    def add_alarm(self, message: Message, hour: str, minute: str, post_to=ch):
        alarm_context = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(post_to) \
            .name(self.name).id(self.id) \
            .day(self.day).hour(hour).minute(minute) \
            .build()

        self.schedule_alarm(alarm_context)

    @listen_to("^%s알람예약취소 (.+)$" % name)
    def cancel_alarm(self, message: Message, post_to=constants.CH_KORDLE_ID):
        self.unschedule_alarm(self.name, self.id, message, post_to)
