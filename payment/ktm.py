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


class KTM(Plugin):
    max_retry = 10
    step = 1
    last_step = 6

    waiter: WebDriverWait
    screenshot_path = os.getcwd() + '/ktm.png'

    id = 'recordame'
    password = 'hahows1003!'

    @listen_to('^더모아 케이티$')
    def kt_m(self, message: Message):
        charge_to_pay = self.pay_kt_m(message)

        if charge_to_pay < 0:
            self.driver.reply_to(message, f'금액 확인 실패')
        else:
            self.driver.reply_to(message, f'{charge_to_pay}원')

    ########################
    def pay_kt_m(self, message: Message) -> int:
        url = 'https://www.ktmmobile.com/mypage/unpaidChargeList.do'

        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('disable-popup-blocking')

        chrome_options.add_experimental_option("detach", True)

        charge_to_pay = -1

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            chrome_driver.implicitly_wait(3)

            self.waiter = WebDriverWait(chrome_driver, 3)
            self.step = 1
            self.last_step = 6

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

                    logging.info('KTM 요금청구 페이지 호출')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] KTM 요금청구 페이지 호출')

                    chrome_driver.get(url)

                    break
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue

            # 로그인 수행
            if self.login_ktm(message, chrome_driver, post_to_update) == -1:
                return -1

            # 금액 확인
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                    return -1
                try:
                    self.step += 1

                    logging.info('금액 확인 중')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 금액 확인 중')
                    charge_info = chrome_driver.find_element(By.ID, 'totalCntReal').get_attribute('value')

                    charge_to_pay = int(charge_info)

                    if charge_to_pay > 0:
                        pass
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

            time.sleep(2)

            screenshot(self.driver, message, chrome_driver, self.screenshot_path)

        return charge_to_pay

    def login_ktm(self, message, chrome_driver, post_to_update):
        # 로그인
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                return -1
            try:
                self.step += 1

                condition = expected_conditions.visibility_of_element_located((By.ID, 'userId'))
                self.waiter.until(condition).send_keys(self.id)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'passWord'))
                self.waiter.until(condition).send_keys(self.password)

                time.sleep(1)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'loginBtn'))
                self.waiter.until(condition).click()

                logging.info('로그인 시도중')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 로그인 시도중')

                break
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue

        require_sms_auth = False

        try:
            condition = expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'c-button--w460'))
            self.waiter.until(condition)

            require_sms_auth = True
        except:
            pass

        if require_sms_auth:
            self.last_step += 3

            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                    return -1
                try:
                    # SMS 인증을 요구 확인
                    self.step += 1

                    logging.info('SMS 인증 요구 탐지')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] SMS 인증 요구 탐지')

                    condition = expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'c-button--w460'))
                    self.waiter.until(condition).click()
                    # SMS 인증 취소
                    self.step += 1

                    condition = expected_conditions.visibility_of_element_located((By.ID, 'smsClosePopBtn'))
                    self.waiter.until(condition).click()

                    logging.info('SMS 인증 취소 중')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] SMS 인증 취소 중')

                    # 재로그인 시도
                    self.step += 1

                    condition = expected_conditions.visibility_of_element_located((By.ID, 'loginBtn'))
                    self.waiter.until(condition).click()

                    logging.info('재로그인 중')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 재로그인 중')

                    time.sleep(1)

                    try:
                        condition = expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'c-button--w460'))
                        self.waiter.until(condition)

                        self.step -= 3

                        continue
                    except:
                        return
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue
