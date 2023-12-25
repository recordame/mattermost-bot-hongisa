from time import sleep

import urllib3
from mmpy_bot import Plugin, listen_to, Message, driver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

urllib3.disable_warnings()


class TheMore(Plugin):
    @listen_to('^더모아 리브엠$')
    def liiv_m(self, message: Message):
        charge_to_pay = pay_liiv_m(self.driver, message)
        self.driver.direct_message(message.user_id, f'{charge_to_pay}원')


########################

def pay_liiv_m(mattermost: driver, message: Message) -> str:
    url = "https://www.liivm.com/mypage/bill/bill/billPayment"

    chrome_options = Options()
    chrome_options.add_argument("headless")
    chrome_options.add_experimental_option("detach", True)

    mattermost.direct_message(message.user_id, 'Step(1/10) 크롬 드라이브 호출')
    chrome_driver = webdriver.Chrome(options=chrome_options)

    for sec in range(1, 4):
        sleep(1)
        mattermost.direct_message(message.user_id, f'Step(2/10) 크롬 드라이브 로드 시작({sec}/3)')

    mattermost.direct_message(message.user_id, 'Step(3/10) 리브엠 청구 페이지 호출')
    chrome_driver.get(url)

    mattermost.direct_message(message.user_id, 'Step(4/10) 로그인 페이지 이동')

    # 아이디 탭으로 이동
    chrome_driver.find_element(by='id', value='loginT3').click()
    mattermost.direct_message(message.user_id, 'Step(5/10) 아이디 탭 이동')

    # 계정 정보 입력
    chrome_driver.find_element(by='id', value='loginUserId').send_keys('recordame')
    chrome_driver.find_element(by='id', value='loginUserIdPw').send_keys('hahows1003!')
    mattermost.direct_message(message.user_id, 'Step(6/10) 계정정보 입력 완료')

    # 페이지 전환 대기
    for sec in range(1, 4):
        sleep(1)
        mattermost.direct_message(message.user_id, f'Step(7/10) 페이지 전환 대기({sec}/3)')

    # 로그인
    chrome_driver.find_element(by='id', value='btnIdLogin').click()
    mattermost.direct_message(message.user_id, 'Step(8/10) 로그인 시도중')

    # 페이지 전환 대기
    for sec in range(1, 11):
        sleep(1)
        mattermost.direct_message(message.user_id, f'Step(9/10) 페이지 전환 대기({sec}/10)')

    charge_to_pay = chrome_driver.find_element(by='id', value='totBillAmt').text.replace('원', '')

    for sec in range(1, 3):
        sleep(1)
        mattermost.direct_message(message.user_id, f'Step(10/10) 금액 가져오는 중 ({sec}/2)')

    if int(charge_to_pay) > 0:
        driver.find_element(by='id', value='btn_paymentSelfLayer').click()
    else:
        pass

    chrome_driver.close()

    return charge_to_pay
