import datetime

import urllib3
from mmpy_bot import Plugin, listen_to, Message
from sphinx.util import requests

urllib3.disable_warnings()


def generate_msg(code):
    msg = '**오늘의 환율** :dollar:\n%s' % get_info(code)

    return msg


class CurrencyAlarm(Plugin):
    @listen_to('^환율(\\s(.+))?$')
    def direct(self, message: Message, *args):
        code = args[1]

        if code is None:
            code = 'USD'

        code.upper()

        self.driver.direct_message(message.user_id, generate_msg(code))


########################

# 서울외국환 중계소
def get_info(code):
    result = None

    for days in range(0, 10):
        if result is not None:
            return result
        else:
            target_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            url = 'http://www.smbs.biz/Flash/TodayExRate_flash.jsp?tr_date=' + target_date

            result = extract_currency(requests.get(url).text, code)


# 미국 원달러 환율 정보 추출
def extract_currency(info: str, code: str):
    result: str = ''

    info = info.replace('\r', '').replace('\n', '')
    print(info)
    if info == '?test0=test&updown=0&loading=ok&':
        return None

    # updown=0&USD=1,303.80&updown1=0&&diff1 =3.6
    idx_start = info.index(code)
    info = info[idx_start:]
    idx_diff = info.index('diff')
    idx_end = info.find('&', idx_diff)

    info = info[:idx_end + 1]

    # USD=1,303.80&updown1=0&&diff1=3.2
    info = info.replace('&&', '&')

    # USD=1,303.80&updown1=0&diff1=3.2
    info_list = info.split('&')

    # [USD=1,303.80, updown1=0, diff1=3.2]
    currency = info_list[0][info_list[0].index("=") + 1:]
    trend = info_list[1][info_list[1].index("=") + 1:]
    diff = str(info_list[2][info_list[2].index("=") + 1:])
    result += (f'- `{code}` 환율: {currency}원\n'
               f'- 전일 대비: '
               f'{("-0." + diff[diff.index(".") + 1:]) if diff.__contains__("-.") else ("+0." + diff[diff.index(".") + 1:]) if diff.__contains__("+.") else diff}원'
               f'{":chart_with_upwards_trend:" if trend == "0" else ":chart_with_downwards_trend:"}')

    return result
