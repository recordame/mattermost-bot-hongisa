import logging
import os
import time

import urllib3
from mmpy_bot import Plugin, listen_to, Message
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from common.utils import update_post, display_progress, screenshot

urllib3.disable_warnings()


class LiivM(Plugin):
    max_retry = 10
    step = 1
    last_step = 5

    waiter: WebDriverWait
    screenshot_path = os.getcwd() + '/liivm.png'

    id = 'recordame'
    password = 'hahows1003!'

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
        # chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('disable-popup-blocking')

        chrome_options.add_experimental_option("detach", True)

        charge_to_pay = -1

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            chrome_driver.implicitly_wait(3)

            self.waiter = WebDriverWait(chrome_driver, 3)
            self.step = 1
            self.last_step = 5

            logging.info('크롬 드라이브 호출')
            reply_msg = self.driver.reply_to(message, f'[{display_progress(self.step, self.last_step)}] 크롬 드라이브 호출')
            post_to_update = reply_msg['id']

            # 요금납부 페이지 호출
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    screenshot(self.driver, message, chrome_driver, self.screenshot_path)
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
            if self.login_liivm(message, chrome_driver, post_to_update) == -1:
                return -1

            # 금액 확인
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                    return -1
                try:
                    self.step += 1

                    condition = expected_conditions.visibility_of_element_located((By.ID, 'totBillAmt'))
                    charge_info = self.waiter.until(condition).text.replace('원', '')
                    charge_to_pay = int(charge_info)

                    logging.info('금액 확인 완료')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 금액 확인 완료')

                    if charge_to_pay > 0:
                        condition = expected_conditions.visibility_of_element_located((By.ID, 'btn_paymentSelfLayer'))
                        self.waiter.until(condition).click()
                    else:
                        pass

                    break
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue

            time.sleep(2)

            screenshot(self.driver, message, chrome_driver, self.screenshot_path)

        return charge_to_pay

    def login_liivm(self, message, chrome_driver, post_to_update):
        # 아이디 비밀번호 기반 로그인 텝으로 이동
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                return -1
            try:
                self.step += 1

                condition = expected_conditions.visibility_of_element_located((By.ID, 'loginT3'))
                self.waiter.until(condition).click()

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
                screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                return -1
            try:
                self.step += 1

                condition = expected_conditions.visibility_of_element_located((By.ID, 'loginUserId'))
                self.waiter.until(condition).send_keys(self.id)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'loginUserIdPw'))
                self.waiter.until(condition).send_keys(self.password)

                time.sleep(1)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'btnIdLogin'))
                self.waiter.until(condition).click()

                logging.info('로그인 시도중')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 로그인 시도중')

                break
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue
