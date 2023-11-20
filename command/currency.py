import urllib
from urllib.request import Request, urlopen

import bs4
import urllib3
from mmpy_bot import Plugin, listen_to, Message

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

# 네이버 환율
def get_info():
    url: str = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=' + urllib.parse.quote(
        '환율')

    req = Request(url)
    page = urlopen(req)
    html = page.read().decode('utf-8')
    soup = bs4.BeautifulSoup(html, 'html.parser')

    return soup


# 미국 원달러 환율 정보 추출
def extract_currency(info: str):
    won_dollar: str
    raw_info = info.find('span', class_='spt_con dw').text.strip(' ').replace('  ', ' ')

    try:
        index = raw_info.find(' 전일대비하락')
        won_dollar = f'- 지수: `{raw_info[:index]}`원\n- 전일: `{raw_info[(index + " 전일대비하락".__len__()):].replace(" ", "▼")}`'
    except:
        index = raw_info.find(' 전일대비상승')
        won_dollar = f'- 지수: `{raw_info[:index]}`원\n- 전일: `{raw_info[(index + " 전일대비상승".__len__()):].replace(" ", "▲")}`'

    return won_dollar
