import datetime
import urllib
from urllib.request import urlopen, Request

import bs4
import urllib3
from mmpy_bot import Message
from mmpy_bot import listen_to

from commons import constant
from commons.abstract_alarm import AbstractAlarm

urllib3.disable_warnings()


# 네이버 날씨 페이지 로드
def get_info(loc: str):
    if loc is None:
        loc = ""

    # 네이버 날씨
    url: str = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query="
    if loc == "":
        url += urllib.parse.quote("날씨")
    else:
        url += urllib.parse.quote(loc) + "+" + urllib.parse.quote("날씨")

    req = Request(url)
    page = urlopen(req)
    html = page.read().decode('utf-8')
    soup = bs4.BeautifulSoup(html, "html.parser")

    return soup


# 날씨정보에 아이콘 추가
def add_icon(status: str):
    if str(status).__contains__('맑음'):
        status += ':sunny:'
    elif str(status).__contains__('구름'):
        status += ':partly_sunny: '
    elif str(status).__contains__('흐림'):
        status += ':cloud:'
    elif str(status).__contains__('비'):
        status += ':umbrella_with_rain_drops:'
    elif str(status).__contains__('눈'):
        status += ':snowflake:'

    return status


# 오늘 날씨 정보 추출
def extract_today(info: str):
    now = datetime.datetime.now()

    try:
        location = info.find('div', class_="title_area").find('h2').text
    except:
        return "지역설정이 잘못 되었습니다."

    today = info.find('div', class_="weather_info").find('div', class_="status_wrap").find('div', class_="_today")
    status = today.find('div', class_="weather_main").find('span', class_="blind").text
    temp = today.find('div', class_="temperature_text").text.replace("현재 온도", "").replace(" ", "")
    temp_yesterday = today.find('div', class_="temperature_info").find('span', class_="temperature").text.removesuffix(" ")
    feel_humidity_wind = today.find('dl', class_="summary_list").text.strip(" ").split(" ")
    particle_uv_sunset = info.find('div', class_="report_card_wrap").text.strip(" ").split(" ")

    # 현재 날씨
    month = str(int(now.strftime("%m")))
    day = str(int(now.strftime("%d")))
    hour = str(int(now.strftime("%H")))

    status = add_icon(str(status))

    msg = "`" + now.strftime(month + "월 " + day + "일 " + hour + "시") + "`\n" \
          + "현재 `" + location + "` 날씨\n" \
          + "- 현재 : " + status + "\n" \
          + "- 기온 : " + temp + "(어제보다 " + temp_yesterday + ")" + "\n"

    # 체감, 습도, 바람 상태
    tmp: str = ""
    i: int = 0

    while i < len(feel_humidity_wind):
        if i % 2 == 0:
            tmp += "- " + feel_humidity_wind[i] + " : "
        else:
            tmp += feel_humidity_wind[i] + "\n"
        i += 1

    # 미세먼지, 초미세먼지, 자외선, 일몰
    i = 0
    while i < len(particle_uv_sunset):
        if particle_uv_sunset[i] != "":
            if i % 2 == 0:
                tmp += "- " + particle_uv_sunset[i] + " : "
            elif i == len(particle_uv_sunset) - 1:
                tmp += particle_uv_sunset[i]
            else:
                tmp += particle_uv_sunset[i] + "\n"

        i += 1

    msg += tmp

    return msg


# 내일 날씨 정보 추출
def extract_tomorrow(info: str):
    status_am = info.find('div', class_="weather_info type_tomorrow").find('ul', class_="weather_info_list _tomorrow").find('div', class_="weather_main").text.strip(" ")
    temp_am = info.find('div', class_="weather_info type_tomorrow").find('ul', class_="weather_info_list _tomorrow").find('div', class_="temperature_text").text.replace("예측 온도", "").replace(" ", "")
    precipitation_am = info.find('div', class_="weather_info type_tomorrow").find('ul', class_="weather_info_list _tomorrow").find('dl', class_="summary_list").text.replace("강수확률", "").strip(" ")
    particle = info.find('div', class_="weather_info type_tomorrow").find('ul', class_="weather_info_list _tomorrow").find('div', class_="report_card_wrap").text.strip(" ").split(" ")
    status_pm = info.find('div', class_="weather_info type_tomorrow").find('div', class_="_pm").find('div', class_="weather_main").text.strip(" ")
    temp_pm = info.find('div', class_="weather_info type_tomorrow").find('div', class_="_pm").find('div', class_="temperature_text").text.replace("예측 온도", "").replace(" ", "")
    precipitation_pm = info.find('div', class_="weather_info type_tomorrow").find('div', class_="_pm").find('dd', class_="desc").text

    status_am = add_icon(str(status_am))
    status_pm = add_icon(str(status_pm))

    msg = "내일 예상 날씨\n" \
          + "- 오전: " + status_am + "\n" \
          + "   - 예상기온 : " + temp_am + "\n" \
          + "   - 강수확률 : " + precipitation_am + "\n" \
          + "- 오후 : " + status_pm + "\n" \
          + "   - 예상기온 : " + temp_pm + "\n" \
          + "   - 강수확률 : " + precipitation_pm + "\n"

    # 미세먼지, 초미세먼지
    tmp: str = ""
    i = 0
    while i < len(particle):
        if particle[i] != "":
            if i % 2 == 0:
                tmp += "- " + particle[i] + " : "
            elif i == len(particle) - 1:
                tmp += particle[i]
            else:
                tmp += particle[i] + "\n"

        i += 1

    msg += tmp

    return msg


class WeatherAlarm(AbstractAlarm):
    name = "날씨"

    def __init__(self):
        self.id = "WeatherAlarm"
        self.day = "mon-sun"
        self.ch = constant.CH_NOTIFICATIONS_ID

    def generate_msg(self, loc: str):
        info = get_info(loc)
        msg = extract_today(info) + "\n" + extract_tomorrow(info)

        return msg

    # 나에게만
    @listen_to("^%s(\s[가-힣]+)?$" % name)
    def direct(self, message: Message, location: str):
        self.alarm(message.user_id, False, location)

    # 전체알림
    @listen_to("^%s알림(\s[가-힣]+)?$" % name)
    def notify(self, message: Message, location: str):
        self.alarm(self.ch, location)

    # 날씨 알림 예약
    @listen_to("^%s알림예약(\s[가-힣]+)? (.+) (.+)$" % name)
    def add_alarm(self, message: Message, location: str, hour: str, minute: str):
        self.schedule_alarm(message, hour, minute, location)

    @listen_to("^%s알림예약취소$" % name)
    def cancel_alarm(self, message: Message):
        self.unschedule_alarm(self.name, message)
