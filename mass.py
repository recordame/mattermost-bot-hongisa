from urllib.request import urlopen, Request

import bs4
import urllib3
from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant
from alarm import Alarm

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


# 채널 알림용 문구 생성
def generate_msg():
    info = get_info()
    mass = extract_mass(info)

    msg = "@here " + mass + "\n" \
          + "평화를 빕니다 :pray:\n" \
          + "https://aos.catholic.or.kr/pro1021/everydayMass"

    return msg


class MassAlarm(Plugin):
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
    @listen_to("^미사알림예약 ([1-9]|1[0-9]|2[0-4])$")
    def add_alarm(self, message: Message, hour: int):
        if self.schedule.get_jobs().__len__() == 1:
            # 기존에 등록된 알림이 있는 경우, 기존 알림 정보 출력
            job = self.schedule.get_jobs()[0]
            alarm: Alarm = constant.ALARMS.get(job.id)

            self.driver.direct_message(message.user_id,
                                       "이미 등록된 알림이 있습니다. `미사알림예약취소` 후 재등록 해주세요.\n\n"
                                       "**알림정보**\n" + alarm.get_info() + "\n"
                                       )
        else:
            # 기존에 등록된 작업이 없는 경우, 새로운 알림 등록 및 시작
            self.driver.direct_message(message.user_id, "미사 알림이 매주 일요일 `%s:00`에 전달됩니다." % (int(hour)))
            self.schedule.add_job(func=lambda: self.driver.create_post(constant.CH_NOTIFICATIONS_ID, generate_msg()),
                                  trigger='cron',
                                  day_of_week='sun',
                                  hour=hour,
                                  minute=00)

            self.schedule.start()

            # 알림 정보 저장
            job = self.schedule.get_jobs()[0]
            alarm = Alarm(message.sender_name, message.user_id, job, "sun", "%s:00" % (int(hour)))
            constant.ALARMS.update({job.id: alarm})

    # 미사 알림 취소
    @listen_to("^미사알림예약취소$")
    def cancel_alarm(self, message: Message):
        # 알림 목록에서 취소할 알림의 정보를 불러와, 알림 생성자에게 삭제 내역 전달
        job = self.schedule.get_jobs()[0]
        alarm: Alarm = constant.ALARMS.get(job.id)
        self.driver.direct_message(alarm.creater_id, "등록하신 미사 알림이 %s님에 의해 삭제되었습니다. \n\n"
                                   % (message.sender_name) + "**알림정보**\n" + alarm.get_info() + "\n")

        # 알림 종료 및 알림 리스트에서 제거
        constant.ALARMS.pop(job.id)

        self.schedule.shutdown()
        self.driver.direct_message(message.user_id, "미사 알림이 종료되었습니다.")
        # 다음 스케쥴 등록을 위해 새로운 스케쥴러 생성
        self.schedule = BackgroundScheduler()
