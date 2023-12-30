import time

import urllib3
from mmpy_bot import Plugin, listen_to, Message
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from common.utils import update_post, display_progress

urllib3.disable_warnings()


class TheMore(Plugin):
    @listen_to('^더모아 리브엠$')
    def liiv_m(self, message: Message):
        charge_to_pay = self.pay_liiv_m(message)

        if charge_to_pay < 0:
            self.driver.reply_to(message, f'금액 확인 실패')
        else:
            self.driver.reply_to(message, f'{charge_to_pay}원')

    ########################
    def pay_liiv_m(self, message: Message) -> int:
        step = 1
        last_step = 7
        max_retry = 10

        url = 'https://www.liivm.com/mypage/bill/bill/billPayment'

        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('disable-popup-blocking')

        chrome_options.add_experimental_option("detach", True)

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            step += 1
            self.driver.reply_to(message, f'[{display_progress(step, last_step)}] 크롬 드라이브 호출')
            post_to_update = self.driver.get_thread(message.id)['order'][1]

            # 요금납부 페이지 호출
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 리브엠 요금청구 페이지 호출')
                    chrome_driver.get(url)

                    break
                except:
                    step -= 1
                    continue

            # 아이디 비밀번호 기반 로그인 텝으로 이동
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    chrome_driver.find_element(by=By.ID, value='loginT3').click()
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 로그인 페이지 이동')

                    break
                except:
                    step -= 1
                    continue

            # 계정 정보 입력
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    chrome_driver.find_element(by=By.ID, value='loginUserId').send_keys('recordame')
                    chrome_driver.find_element(by=By.ID, value='loginUserIdPw').send_keys('hahows1003!')
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 계정정보 입력 완료')

                    break
                except:
                    step -= 1
                    continue

            # 로그인
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    chrome_driver.find_element(by=By.ID, value='btnIdLogin').click()
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 로그인 시도중')

                    break
                except:
                    step -= 1
                    time.sleep(0.5)
                    continue

            # 금액 확인
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    charge_to_pay = int(chrome_driver.find_element(by=By.ID, value='totBillAmt').text.replace('원', ''))
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 금액 확인 중')

                    if charge_to_pay > 0:
                        chrome_driver.find_element(by=By.ID, value='btn_paymentSelfLayer').click()
                    else:
                        pass

                    break
                except:
                    step -= 1
                    time.sleep(0.5)
                    continue

            step += 1
            update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 금액 확인 완료')

        return charge_to_pay

    @listen_to('^더모아 케이티$')
    def kt_m(self, message: Message):
        charge_to_pay = self.pay_kt_m(message)

        if charge_to_pay < 0:
            self.driver.reply_to(message, f'금액 확인 실패')
        else:
            self.driver.reply_to(message, f'{charge_to_pay}원')

    ########################
    def pay_kt_m(self, message: Message) -> int:
        step = 1
        last_step = 9
        max_retry = 10

        url = 'https://www.ktmmobile.com/mypage/unpaidChargeList.do'

        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('disable-popup-blocking')

        chrome_options.add_experimental_option("detach", True)

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            step += 1
            self.driver.reply_to(message, f'[{display_progress(step, last_step)}] 크롬 드라이브 호출')
            post_to_update = self.driver.get_thread(message.id)['order'][1]

            # 요금납부 페이지 호출
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] KTM 요금청구 페이지 호출')
                    chrome_driver.get(url)

                    break
                except:
                    step -= 1
                    continue

            # 로그인
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    chrome_driver.find_element(by=By.ID, value='userId').send_keys('recordame')
                    chrome_driver.find_element(by=By.ID, value='passWord').send_keys('lkg0473PA!')
                    chrome_driver.find_element(by=By.ID, value='loginBtn').click()

                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 로그인 시도중')

                    break
                except:
                    step -= 1
                    time.sleep(0.5)
                    continue

            # SMS 인증을 요구 확인
            for retry in range(max_retry):
                try:
                    step += 1
                    chrome_driver.find_element(by=By.CLASS_NAME, value='c-button--w460').click()
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] SMS 인증 요구 탐지')

                    break
                except:
                    time.sleep(1)
                    step -= 1
                    continue

            # SMS 인증 취소
            for retry in range(max_retry):
                try:
                    step += 1
                    chrome_driver.find_element(by=By.ID, value='smsClosePopBtn').click()
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] SMS 인증 취소 중')

                    break
                except:
                    time.sleep(1)
                    step -= 1
                    continue

            # 재로그인 시도
            for retry in range(max_retry):
                try:
                    step += 1
                    chrome_driver.find_element(by=By.ID, value='loginBtn').click()
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 재로그인 중')

                    break
                except:
                    time.sleep(1)
                    step -= 1
                    continue

            # 금액 확인
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    charge_to_pay = int(chrome_driver.find_element(by=By.ID, value='totalCnt').text.replace('원', ''))
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 금액 확인 중')

                    if charge_to_pay > 0:
                        pass
                    else:
                        pass

                    break
                except:
                    step -= 1
                    time.sleep(0.5)
                    continue

            step += 1
            update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 금액 확인 완료')
        return charge_to_pay

    @listen_to('^더모아 인터넷$')
    def internet(self, message: Message):
        charge_to_pay = self.pay_internet(message)

        if charge_to_pay < 0:
            self.driver.reply_to(message, f'금액 확인 실패')
        else:
            self.driver.reply_to(message, f'{charge_to_pay}원')

    ########################
    def pay_internet(self, message: Message) -> int:
        step = 1
        last_step = 8
        max_retry = 10

        url = 'https://www.lguplus.com/mypage/payinfo?p=1'

        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('disable-popup-blocking')

        chrome_options.add_experimental_option("detach", True)

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            step += 1
            self.driver.reply_to(message, f'[{display_progress(step, last_step)}] 크롬 드라이브 호출')
            post_to_update = self.driver.get_thread(message.id)['order'][1]

            # 요금납부 페이지 호출
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] LG U+ 요금청구 페이지 호출')
                    chrome_driver.get(url)

                    break
                except:
                    step -= 1
                    continue

            # 로그인 방법 선택 U+ID
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    chrome_driver.find_element(by=By.ID, value='_uid_236').click()

                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] U+ID 로그인 선택')

                    break
                except:
                    step -= 1
                    time.sleep(0.5)
                    continue

            time.sleep(2)

            # 로그인
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    found = False

                    chrome_driver.find_element(by=By.ID, value='username-1-6').clear()
                    chrome_driver.find_element(by=By.ID, value='password-1').clear()

                    chrome_driver.find_element(by=By.ID, value='username-1-6').send_keys('recordame@naver.com')
                    chrome_driver.find_element(by=By.ID, value='password-1').send_keys('lkg0473PA!')

                    for btn in chrome_driver.find_elements(by=By.TAG_NAME, value='button'):
                        if btn.text.__contains__('로그인'):
                            btn.click()
                            update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 로그인 시도중')
                            found = True

                            time.sleep(3)

                            break
                    if not found:
                        raise Exception

                    break
                except:
                    step -= 1
                    time.sleep(0.5)
                    continue

            time.sleep(2)

            # 요금바로 납부 선택
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    found = False

                    for btn in chrome_driver.find_elements(by=By.TAG_NAME, value='button'):
                        if btn.text == '요금바로 납부':
                            btn.click()
                            update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 요금 바로 납부 요청')
                            found = True

                            break

                    if not found:
                        raise Exception

                    break
                except:
                    step -= 1
                    time.sleep(0.5)
                    continue

            time.sleep(2)

            # 금액 확인
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    try:
                        charge_to_pay = int(chrome_driver.find_element(by=By.CLASS_NAME, value='pay-total-txt').text.replace('원', ''))
                    except ValueError:
                        charge_to_pay = 0

                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 금액 확인 중')

                    if charge_to_pay > 0:
                        pass
                    else:
                        pass

                    break
                except:
                    step -= 1
                    time.sleep(0.5)
                    continue

            step += 1
            update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 금액 확인 완료')

        return charge_to_pay
