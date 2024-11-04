import urllib
from datetime import datetime
from urllib.request import urlopen, Request

import bs4
from mmpy_bot import listen_to, Message

from alarm.alarm_context import AlarmContextBuilder
from alarm.builtin.abstract_builtin_alarm import AbstractChannelAlarm
from common import constant
from common.utils import get_today_str

default_loc = '송파구풍납2동'


class WeatherAlarm(AbstractChannelAlarm):
    name = '날씨'
    id = 'weather'
    day = 'mon-sun'

    channel_id = constant.CH_NOTIFICATIONS_ID

    def __init__(self):
        super().__init__()
        self.register_instance(self.name, self)

    def generate_message(self, *args):
        loc: str = args[0][0]

        if (loc is None) or len(loc) == 0:
            loc = default_loc

        info = load_web_page(loc)
        msg = extract_today_weather_information(info)

        return msg

    @listen_to('^%s$' % name)
    def default_location(self, message: Message):
        self.driver.direct_message(message.user_id, self.generate_message([default_loc]))

    @listen_to('^%s\\s([가-힣]+)$' % name)
    def direct(self, message: Message, location: str):
        self.driver.direct_message(message.user_id, self.generate_message([location.strip(' ')]))

    @listen_to(
        '^%s알람등록'
        '\\s([가-힣]+)'  # 지역
        '\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)'  # 시
        '\\s([\\*|\\*/\\d|\\d|\\-|\\,]+)$'  # 분
        % name
    )
    def add_alarm(self, message: Message, location: str, hour: str, minute: str, recovery_mode: bool = False):
        alarm_context = AlarmContextBuilder() \
            .creator_name(message.sender_name).creator_id(message.user_id).post_to(self.channel_id) \
            .name(self.name).id(self.id) \
            .day(self.day).hour(hour).minute(minute) \
            .message(location) \
            .build()

        self.schedule_alarm(alarm_context, recovery_mode)

    @listen_to('^%s알람취소$' % name)
    def cancel_alarm(self, message: Message, post_to=channel_id):
        self.unschedule_alarm(self.name, self.id, message, post_to)


##################################

def load_web_page(loc: str = default_loc):
    # 네이버 날씨
    url: str = f'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query={urllib.parse.quote(f"{loc}+날씨")}'

    req = Request(url)
    page = urlopen(req)

    html = page.read().decode('utf-8')
    soup = bs4.BeautifulSoup(html, 'html.parser')

    return soup


def extract_today_weather_information(info):
    try:
        location = info \
            .find('div', class_='title_area') \
            .find('h2') \
            .text
    except:
        return '지역설정이 잘못 되었습니다.'

    today = info \
        .find('div', class_='weather_info') \
        .find('div', class_='status_wrap') \
        .find('div', class_='_today')

    status = today \
        .find('div', class_='weather_main') \
        .find('span', class_='blind') \
        .text

    temp = today \
        .find('div', class_='temperature_text') \
        .text \
        .replace('현재 온도', '') \
        .replace(' ', '')

    temp_yesterday = today \
        .find('div', class_='temperature_info') \
        .find('span', class_='temperature') \
        .text \
        .removesuffix(" ")

    temp_lowest = info \
        .find('div', class_='list_box _weekly_weather') \
        .find('li', class_='week_item today') \
        .find('div', class_='cell_temperature') \
        .find('span', class_='lowest') \
        .text \
        .replace('최저기온', '')

    temp_highest = info \
        .find('div', class_='list_box _weekly_weather') \
        .find('li', class_='week_item today') \
        .find('div', class_='cell_temperature') \
        .find('span', class_='highest') \
        .text \
        .replace('최고기온', '')

    particle_info = info \
        .find('div', class_='report_card_wrap') \
        .find('ul', class_='today_chart_list')

    fine_particle = ''
    ultra_fine_particle = ''

    for pm in particle_info:
        if pm.text.strip().startswith('미세'):
            fine_particle = pm.text.replace('미세먼지', '').strip()
        elif pm.text.strip().startswith('초미세'):
            ultra_fine_particle = pm.text.replace('초미세먼지', '').strip()

    status = add_icon(str(status))

    today = datetime.now()

    msg = '@here `%s`\n' % get_today_str() + \
          f'**`{location}`** 날씨정보' + \
          '\n\n-----------------------------\n' + \
          f'**현재 날씨**는 {status}, **기온**은 `{temp}`예요.\n오늘 **최저** `{temp_lowest}`, **최고** `{temp_highest}`로 예상돼요.\n* 미세먼지 {add_icon(fine_particle)}\n* 초미세먼지 {add_icon(ultra_fine_particle)}'

    return msg


def extract_tomorrow_weather_information(info):
    status_am = info.find('div', class_='weather_info type_tomorrow') \
        .find('ul', class_='weather_info_list _tomorrow') \
        .find('div', class_='weather_main') \
        .text \
        .strip(' ')

    temp_am = info \
        .find('div', class_='weather_info type_tomorrow') \
        .find('ul', class_='weather_info_list _tomorrow') \
        .find('div', class_='temperature_text') \
        .text \
        .replace('예측 온도', '') \
        .replace(' ', '')

    precipitation_am = info \
        .find('div', class_='weather_info type_tomorrow') \
        .find('ul', class_='weather_info_list _tomorrow') \
        .find('dl', class_='summary_list') \
        .text \
        .replace('강수확률', '') \
        .strip(' ')

    status_pm = info \
        .find('div', class_='weather_info type_tomorrow') \
        .find('div', class_='_pm') \
        .find('div', class_='weather_main') \
        .text \
        .strip(' ')

    temp_pm = info \
        .find('div', class_='weather_info type_tomorrow') \
        .find('div', class_='_pm') \
        .find('div', class_='temperature_text') \
        .text \
        .replace('예측 온도', '') \
        .replace(' ', '')

    precipitation_pm = info \
        .find('div', class_='weather_info type_tomorrow') \
        .find('div', class_='_pm').find('dd', class_='desc') \
        .text

    particle_info = info \
        .find('div', class_='weather_info type_tomorrow') \
        .find('ul', class_='weather_info_list _tomorrow') \
        .find('div', class_='report_card_wrap') \
        .find('ul', class_='today_chart_list')

    fine_particle = ''
    ultra_fine_particle = ''

    for pm in particle_info:
        if pm.text.strip().startswith('미세'):
            fine_particle = pm.text.replace('미세먼지', '').strip()
        elif pm.text.strip().startswith('초미세'):
            ultra_fine_particle = pm.text.replace('초미세먼지', '').strip()

    msg = '**내일요약**\n**오전**: %s, **기온**: `%s`, **강수**: `%s`\n**오후**: %s, **기온**: `%s`, **강수**: `%s`\n* 미세먼지 %s\n* 초미세먼지 %s' \
          % (add_icon(str(status_am)), temp_am, precipitation_am, add_icon(str(status_pm)), temp_pm, precipitation_pm,
             add_icon(fine_particle), add_icon(ultra_fine_particle))

    return msg


# 날씨 아이콘 설정
def add_icon(status: str):
    if str(status).__contains__('맑음'):
        status += ' :sunny: '
    elif str(status).__contains__('구름'):
        status += ' :partly_sunny: '
    elif str(status).__contains__('흐림'):
        status += ' :cloud: '
    elif str(status).__contains__('비'):
        status += ':umbrella_with_rain_drops: '
    elif str(status).__contains__('눈'):
        status += ' :snowflake: '
    elif str(status).__contains__('나쁨'):
        status = ' :red_circle:'
    elif str(status).__contains__('보통'):
        status = ' :large_green_circle: '
    elif str(status).__contains__('좋음'):
        status = ' :large_blue_circle: '

    return status
