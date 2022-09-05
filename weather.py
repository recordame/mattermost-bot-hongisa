import datetime
import urllib
from urllib.request import urlopen, Request

import bs4
import schedule
from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to

import constant


## 날씨 정보 얻기
def weather_info(loc: str = ""):
    now = datetime.datetime.now()

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

    location = soup.find('div', class_="title_area").find('h2').text
    today = soup.find('div', class_="weather_info").find('div', class_="status_wrap").find('div', class_="_today")
    status = today.find('div', class_="weather_main").find('span', class_="blind").text
    temp = today.find('div', class_="temperature_text").text.replace("현재 온도", "").replace(" ", "")
    temp_yesterday = today.find('div', class_="temperature_info").find('span', class_="temperature").text.removesuffix(" ")
    summary_list = today.find('dl', class_="summary_list").text.strip(" ").split(" ")

    # 현재 날씨
    month = str(int(now.strftime("%m")))
    day = str(int(now.strftime("%d")))
    hour = str(int(now.strftime("%H")))
    minute = str(int(now.strftime("%M")))
    second = str(int(now.strftime("%S")))

    msg = "@here **" + now.strftime(month + "월 " + day + "일 " + hour + "시 " + minute + "분 " + second + "초") + "**" \
          + " 현재 **" + location + "**의 날씨 입니다.\n" \
          + "- 현재 : " + status + "\n" \
          + "- 기온 : " + temp + "(어제보다 " + temp_yesterday + ")" + "\n"

    # 체감, 습도, 바람 상태
    tmp: str = ""
    i: int = 0
    while i < len(summary_list):
        if i % 2 == 0:
            tmp += "- " + summary_list[i] + " : "
        elif i == len(summary_list) - 1:
            tmp += summary_list[i]
        else:
            tmp += summary_list[i] + "\n"
        i += 1

    msg += tmp

    return msg


class Weather(Plugin):
    ## 스켸쥴링시 날씨 정보를 갱신해서 가지고 오는 부분
    def alarm_funcs(self, message: Message):
        msg = weather_info()
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

    ## 필요시
    @listen_to("^날씨 ([가-힣]+)$")
    def weather_loc(self, message: Message, loc: str):
        self.weather(message, loc)

    @listen_to("^날씨$")
    def weather(self, message: Message, loc: str = ""):
        self.driver.direct_message(message.user_id, weather_info(loc))
