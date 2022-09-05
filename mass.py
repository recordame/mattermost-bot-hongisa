import datetime
import urllib
from urllib.request import urlopen, Request

import bs4
import schedule
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


def get_info():
    # 서울대교구
    url: str = "https://aos.catholic.or.kr/pro1021/everydayMass"

    req = Request(url)
    page = urlopen(req)
    html = page.read().decode('utf-8')
    soup = bs4.BeautifulSoup(html, "html.parser")

    return soup


def extract_mass(info: str):
    today = info.find('p', class_="bibleBox").text.replace("  ", " ")
    mass_day = info.find('em').text
    mass_title = info.find('p', class_="bibleTit").text;

    msg = "``" + today + "``" + "\n**" + mass_day + "**\n >" + mass_title + "\n"

    return msg


class Mass(Plugin):
    @listen_to("^미사알림$")
    def mass(self, message: Message):
        info = get_info()
        mass = extract_mass(info)

        msg = "@here " + mass + "\n" \
              + "평화를 빕니다 :pray:\n" \
              + "https://aos.catholic.or.kr/pro1021/everydayMass"

        self.driver.create_post(constant.CH_NOTIFICATIONS_ID, msg)

    @listen_to("^미사알림시작 (1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24)$")
    def mass_alarm(self, message: Message, at: str):
        oclock: str = str('{:02d}'.format(int(at))) + ":00"

        now = datetime.datetime.now()

        msg = "@here\n" \
              + "미사 시간입니다. 평화를 빕니다 :pray:\n" \
              + "https://aos.catholic.or.kr/pro1021/everydayMass"

        self.driver.direct_message(message.user_id, "미사 알림이 매주 일요일 ``" + oclock + "``시에 전달됩니다.")

        schedule.every().sunday.at(oclock).do(
            self.driver.create_post, constant.CH_KORDLE_ID, msg
        )

    @listen_to("^미사알림종료$")
    def cancel_jobs(self, message: Message):
        schedule.clear()

        self.driver.direct_message(message.user_id, "미사 알림이 종료되었습니다.")
