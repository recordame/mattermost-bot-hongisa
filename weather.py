import datetime
import urllib
from urllib.request import urlopen, Request

import bs4
import schedule
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


## 전체 날씨 정보
def get_info(loc: str = ""):
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


## 오늘 날씨 정보
def get_today(info: str):
    now = datetime.datetime.now()

    location = info.find('div', class_="title_area").find('h2').text
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
    minute = str(int(now.strftime("%M")))
    second = str(int(now.strftime("%S")))

    msg = "``" + now.strftime(month + "월 " + day + "일 " + hour + "시 " + minute + "분 " + second + "초") + "``\n" \
          + "현재 ``" + location + "``의 날씨 입니다.\n" \
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


## 내일 날씨 정보
def get_tomorrow(info: str):
    status_am = info.find('div', class_="weather_info type_tomorrow").find('ul', class_="weather_info_list _tomorrow").find('div', class_="weather_main").text.strip(" ")
    temp_am = info.find('div', class_="weather_info type_tomorrow").find('ul', class_="weather_info_list _tomorrow").find('div', class_="temperature_text").text.replace("예측 온도", "").replace(" ", "")
    precipitation_am = info.find('div', class_="weather_info type_tomorrow").find('ul', class_="weather_info_list _tomorrow").find('dl', class_="summary_list").text.replace("강수확률", "").strip(" ")
    particle = info.find('div', class_="weather_info type_tomorrow").find('ul', class_="weather_info_list _tomorrow").find('div', class_="report_card_wrap").text.strip(" ").split(" ")
    status_pm = info.find('div', class_="weather_info type_tomorrow").find('div', class_="_pm").find('div', class_="weather_main").text.strip(" ")
    temp_pm = info.find('div', class_="weather_info type_tomorrow").find('div', class_="_pm").find('div', class_="temperature_text").text.replace("예측 온도", "").replace(" ", "")
    precipitation_pm = info.find('div', class_="weather_info type_tomorrow").find('div', class_="_pm").find('dd', class_="desc").text

    msg = "내일 예상 날씨 입니다.\n" \
          + "- 오전\n" \
          + "   - 예상 : " + status_am + "\n" \
          + "   - 기온 : " + temp_am + "\n" \
          + "   - 강수 : " + precipitation_am + "\n" \
          + "- 오후\n" \
          + "   - 예상 : " + status_pm + "\n" \
          + "   - 기온 : " + temp_pm + "\n" \
          + "   - 강수 : " + precipitation_pm + "\n"

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


class Weather(Plugin):
    @listen_to("^날씨$")
    def weather(self, message: Message, loc: str = ""):
        info = get_info(loc);
        msg = get_today(info) + "\n" + get_tomorrow(info)

        self.driver.direct_message(message.user_id, msg)

    ## 필요시
    @listen_to("^날씨 ([가-힣]+)$")
    def weather_at_location(self, message: Message, loc: str):
        self.weather(message, loc)

    ## 스케줄링시 날씨 정보를 갱신해서 가지고 오는 부분
    def alarm_funcs(self, message: Message):
        info = get_info();
        msg = get_today(info) + "\n" + get_tomorrow(info)

        self.driver.create_post(constant.CH_NOTIFICATIONS_ID, msg)

    ## 스케쥴링
    @listen_to("^날씨알림 (1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24)$")
    def weather_alarm(self, message: Message, at: str):
        self.driver.direct_message(message.user_id, "날씨 알림이 매일 " + at + "시간마다 전달됩니다.")

        schedule.every(int(at)).hours.do(
            self.alarm_funcs, message
        )

    @listen_to("^날씨종료$")
    def cancel_jobs(self, message: Message):
        schedule.clear()
        self.driver.direct_message(message.user_id, "날씨 알림이 종료되었습니다.")
