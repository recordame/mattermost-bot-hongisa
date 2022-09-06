from urllib.request import urlopen, Request

import bs4
import urllib3
from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant

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

    msg = "``" + today + "``" + "\n**" + mass_day + "**\n >" + mass_title + "\n"

    return msg


# 채널 알림용 문구 생성
def generate_msg():
    info = get_info()
    mass = extract_mass(info)

    msg = "@here " + mass + "\n" \
          + "평화를 빕니다 :pray:\n" \
          + "https://aos.catholic.or.kr/pro1021/everydayMass"

    return msg


class Mass(Plugin):
    schedule = BackgroundScheduler()

    # 나에게만
    @listen_to("^미사$")
    def direct(self, message: Message):
        self.driver.direct_message(message.user_id, generate_msg())

    # 전체공유
    @listen_to("^미사알림$")
    def notify(self, message: Message):
        self.driver.create_post(constant.CH_NOTIFICATIONS_ID, generate_msg())

    # 미사 알림 예약
    @listen_to("^미사예약 ([1-9]|1[0-9]|2[0-4])$")
    def add_alarm(self, message: Message, at: int):
        self.schedule.add_job(func=lambda: self.driver.create_post(constant.CH_NOTIFICATIONS_ID, generate_msg()),
                              trigger='cron',
                              day_of_week='sun',
                              hour=at,
                              minute=00)

        oclock: str = str(at) + ":00"
        self.driver.direct_message(message.user_id, "미사 알림이 매주 일요일 ``" + oclock + "``시에 전달됩니다.")

        self.schedule.start()
        constant.JOBS.append(self.schedule.get_jobs())

    # 미사 알림 종료
    @listen_to("^미사예약취소$")
    def cancel_alarm(self, message: Message):
        constant.JOBS.remove(self.schedule.get_jobs())
        self.schedule.shutdown()
        self.driver.direct_message(message.user_id, "미사 알림이 종료되었습니다.")
