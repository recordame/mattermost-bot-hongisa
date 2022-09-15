from urllib.request import urlopen, Request

import bs4
import urllib3
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

from commons import constant
from commons.alarm import Alarm

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
    alarm_id: str = "MassAlarm"
    alarm_name: str = "미사"
    alarm_day: str = "sun"
    alarm_text: str = generate_msg()

    # 나에게만
    @listen_to("^%s$" % alarm_name)
    def direct(self, message: Message):
        self.driver.direct_message(message.user_id, generate_msg())

    # 전체공유
    @listen_to("^%s알림$" % alarm_name)
    def notify(self, message: Message):
        self.driver.create_post(constant.CH_NOTIFICATIONS_ID, generate_msg())

    # 미사 알림 예약
    @listen_to("^%s알림예약 ([1-9]|1[0-9]|2[0-4])$" % alarm_name)
    def add_alarm(self, message: Message, hour: int):
        # 기존에 등록된 알림 여부 확인
        job = constant.SCHEDULE.get_job(self.alarm_id)

        if job is not None:
            # 기존에 등록된 알림이 있는 경우, 기존 알림 정보 출력
            alarm: Alarm = constant.ALARMS.get(job.id)

            self.driver.direct_message(message.user_id,
                                       "이미 등록된 알림이 있습니다. `%s예약취소` 후 재등록 해주세요.\n"
                                       "**알림정보**\n"
                                       "%s\n"
                                       % (self.alarm_name, alarm.get_info()))
        else:
            # 기존에 등록된 작업이 없는 경우, 새로운 알림 등록 및 시작
            self.driver.direct_message(message.user_id, "`%s` 알림이 `%s %d:%02d`에 전달됩니다." % (self.alarm_name, self.alarm_day, int(hour), "00"))
            constant.SCHEDULE.add_job(id=self.alarm_id,
                                      func=lambda: self.driver.create_post(constant.CH_NOTIFICATIONS_ID, generate_msg()),
                                      trigger='cron',
                                      day_of_week=self.alarm_day,
                                      hour=hour,
                                      minute=00)

            job = constant.SCHEDULE.get_job(self.alarm_id)

            # 알림 정보 저장
            alarm = Alarm(message.sender_name, message.user_id, job.id, self.alarm_day, "%s:00" % (int(hour)))
            constant.ALARMS.update({job.id: alarm})

    # 미사 알림 취소
    @listen_to("^%s알림예약취소$" % alarm_name)
    def cancel_alarm(self, message: Message):
        job = constant.SCHEDULE.get_job(self.alarm_id)

        if job is not None:
            # 알림 목록에서 취소할 알림의 정보를 불러와, 알림 생성자에게 삭제 내역 전달
            alarm: Alarm = constant.ALARMS.get(job.id)

            self.driver.direct_message(alarm.creator_id,
                                       "등록하신 `%s` 알림이 %s님에 의해 삭제되었습니다.\n\n"
                                       "**알림정보**\n"
                                       "%s\n"
                                       % (message.sender_name, self.alarm_name, alarm.get_info()))

            # 알림 리스트 및 백그라운드 스케쥴에서 제거
            constant.ALARMS.pop(job.id)
            constant.SCHEDULE.remove_job(job.id)

            self.driver.direct_message(message.user_id, "`%s` 알림이 종료되었습니다." % self.alarm_name)
        else:
            self.driver.direct_message(message.user_id, "등록된 알림이 없습니다.")
