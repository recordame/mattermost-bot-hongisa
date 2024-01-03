import logging
import time

import urllib3
from mmpy_bot import Plugin, listen_to, Message
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from common.utils import update_post, display_progress

urllib3.disable_warnings()


class LiivM(Plugin):
    step = 0
    last_step = 7
    max_retry = 10

    @listen_to('^더모아 리브엠$')
    def liiv_m(self, message: Message):
        charge_to_pay = self.pay_liiv_m(message)

        if charge_to_pay < 0:
            self.driver.reply_to(message, f'금액 확인 실패')
        else:
            self.driver.reply_to(message, f'{charge_to_pay}원')

    ########################
    def pay_liiv_m(self, message: Message) -> int:
        url = 'https://www.liivm.com/mypage/bill/bill/billPayment'

        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('disable-popup-blocking')

        chrome_options.add_experimental_option("detach", True)

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            self.step = 1

            logging.info('크롬 드라이브 호출')
            reply_msg = self.driver.reply_to(message, f'[{display_progress(self.step, self.last_step)}] 크롬 드라이브 호출')
            post_to_update = reply_msg['id']

            # 요금납부 페이지 호출
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    return -1

                try:
                    self.step += 1

                    logging.info('리브엠 요금청구 페이지 호출')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 리브엠 요금청구 페이지 호출')
                    chrome_driver.get(url)

                    break
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue

            # 로그인
            self.login_liivm(chrome_driver, post_to_update)

            # 금액 확인
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    return -1

                try:
                    self.step += 1

                    charge_to_pay = int(WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'totBillAmt'))).text.replace('원', ''))

                    logging.info('금액 확인 중')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 금액 확인 중')

                    if charge_to_pay > 0:
                        chrome_driver.find_element(by=By.ID, value='btn_paymentSelfLayer').click()
                    else:
                        pass

                    break
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue

            self.step += 1

            logging.info('금액 확인 완료')
            update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 금액 확인 완료')

        return charge_to_pay

    def login_liivm(self, chrome_driver, post_to_update):
        # 아이디 비밀번호 기반 로그인 텝으로 이동
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                return -1

            try:
                self.step += 1
                WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'loginT3'))).click()

                logging.info('로그인 페이지 이동')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 로그인 페이지 이동')

                break
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue

        # 계정 정보 입력
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                return -1

            try:
                self.step += 1

                WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'loginUserId'))).send_keys('recordame')
                WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'loginUserIdPw'))).send_keys('hahows1003!')

                logging.info('계정정보 입력')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 계정정보 입력 완료')

                break
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue

        # 로그인
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                return -1

            try:
                self.step += 1

                WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'btnIdLogin'))).click()

                logging.info('로그인 시도중')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 로그인 시도중')

                break
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue
