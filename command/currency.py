import datetime

import urllib3
from mmpy_bot import Plugin, listen_to, Message
from sphinx.util import requests

urllib3.disable_warnings()


def generate_msg():
    info = get_info()
    msg = '**오늘의 환율** :dollar:\n%s' % extract_currency(info)

    return msg


class CurrencyAlarm(Plugin):
    @listen_to('^환율$')
    def direct(self, message: Message):
        self.driver.direct_message(message.user_id, generate_msg())


########################

# 서울외국환 중계소
def get_info():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    url: str = 'http://www.smbs.biz/Flash/TodayExRate_flash.jsp?tr_date=' + today

    result = extract_currency(requests.get(url).text)

    for days in range(1, 10):
        if result is not None:
            return result
        else:
            one_day_before = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            url = 'http://www.smbs.biz/Flash/TodayExRate_flash.jsp?tr_date=' + one_day_before

            result = extract_currency(requests.get(url).text)


# 미국 원달러 환율 정보 추출
def extract_currency(info: str):
    result: str = ''

    if info.replace('\r', '').replace('\n', '') == '?test0=test&updown=0&loading=ok&':
        return None

    # updown=0&USD=1,303.80&updown1=0&&diff1 =3.6
    idx_start = info.index('USD')
    info = info[idx_start:]
    idx_diff = info.index('diff')
    idx_end = info.find('&', idx_diff)

    info = info[:idx_end + 1]

    # USD=1,303.80&updown1=0&&diff1=3.2
    info = info.replace('&&', '&')

    # USD=1,303.80&updown1=0&diff1=3.2
    info_list = info.split('&')

    # [USD=1,303.80, updown1=0, diff1=3.2]
    result += f'원달러 환율: {info_list[0][info_list[0].index("=") + 1:]}원'
    result += f'{"▲" if info_list[1][info_list[1].index("=") + 1:] == "0" else "▼"}'
    result += f'{info_list[2][info_list[2].index("=") + 1:]}'

    return result
