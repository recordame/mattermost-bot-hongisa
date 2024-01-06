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


class LGU(Plugin):
    max_retry = 10
    step = 1
    last_step = 7

    waiter: WebDriverWait

    screenshot_path = os.getcwd() + 'lgu.png'

    id = 'recordame@naver.com'
    password = 'lkg0473PA!'

    @listen_to('^더모아 인터넷$')
    def internet(self, message: Message):
        charge_to_pay = self.pay_internet(message)

        if charge_to_pay < 0:
            self.driver.reply_to(message, f'금액 확인 실패')
        else:
            self.driver.reply_to(message, f'{charge_to_pay}원')

    ########################
    def pay_internet(self, message: Message) -> int:
        url = 'https://www.lguplus.com/mypage/payinfo?p=1'

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
            self.last_step = 7

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

                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] LG U+ 요금청구 페이지 호출')
                    chrome_driver.get(url)

                    logging.info('LG U+ 요금청구 페이지 호출')

                    break
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue

            # 로그인
            if self.login_lgu(message, chrome_driver, post_to_update) == -1:
                return -1

            # 요금바로 납부 선택
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                    return -1
                try:
                    self.step += 1

                    condition = expected_conditions.visibility_of_element_located((By.XPATH, '// button[text()="요금바로 납부"]'))
                    self.waiter.until(condition).click()

                    break
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue

            # 금액 확인
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                    return -1
                try:
                    self.step += 1

                    try:
                        condition = expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'pay-total-txt'))
                        charge_info = self.waiter.until(condition).text.replace('원', '')
                        charge_to_pay = int(charge_info)
                    except ValueError:
                        charge_to_pay = 0

                    logging.info('금액 확인 중')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 금액 확인 중')

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

    def login_lgu(self, message, chrome_driver, post_to_update):
        # 로그인 방법 선택 U+ID
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                return -1
            try:
                self.step += 1

                condition = expected_conditions.visibility_of_element_located((By.XPATH, '// img[@alt="u+ID"]'))
                element = self.waiter.until(condition)
                element = element.find_element(By.XPATH, '..')
                element.click()

                logging.info('U+ID 로그인 선택')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] U+ID 로그인 선택')

                break
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue

        # 로그인
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                screenshot(self.driver, message, chrome_driver, self.screenshot_path)
                return -1
            try:
                self.step += 1

                condition = expected_conditions.visibility_of_element_located((By.ID, 'username-1-6'))
                self.waiter.until(condition).clear()

                condition = expected_conditions.visibility_of_element_located((By.ID, 'password-1'))
                self.waiter.until(condition).clear()

                time.sleep(1)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'username-1-6'))
                self.waiter.until(condition).send_keys(self.id)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'password-1'))
                self.waiter.until(condition).send_keys(self.password)

                time.sleep(1)

                condition = expected_conditions.visibility_of_element_located((By.XPATH, '// button[contains(., "ID 로그인")]'))
                self.waiter.until(condition).click()

                logging.info('로그인 시도중')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 로그인 시도중')

                time.sleep(5)

                try:
                    condition = expected_conditions.visibility_of_element_located((By.XPATH, '// button[contains(., "ID 로그인")]'))
                    self.waiter.until(condition)

                    chrome_driver.refresh()

                    self.step -= 1

                    continue
                except:
                    return
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue
