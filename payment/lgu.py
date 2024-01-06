import logging
import os

import urllib3
from mmpy_bot import Plugin, listen_to, Message
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from common.utils import update_post, display_progress, full_screenshot

urllib3.disable_warnings()


class LGU(Plugin):
    max_retry = 10
    step = 1
    last_step = 7

    waiter: WebDriverWait

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

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            chrome_driver.implicitly_wait(10)

            self.waiter = WebDriverWait(chrome_driver, 10)
            self.step = 1
            self.last_step = 7

            logging.info('크롬 드라이브 호출')
            reply_msg = self.driver.reply_to(message, f'[{display_progress(self.step, self.last_step)}] 크롬 드라이브 호출')
            post_to_update = reply_msg['id']

            # 요금납부 페이지 호출
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
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
            self.login_lgu(message, chrome_driver, post_to_update)

            # 요금바로 납부 선택
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    self.screenshot(message, chrome_driver, os.getcwd() + 'afterLogin-lgu.png')
                    return -1
                try:
                    self.step += 1

                    element = chrome_driver.find_element(By.XPATH, "//*[text()='요금바로 납부']")
                    element.click()

                    # found = False

                    # for btn in chrome_driver.find_elements(by=By.TAG_NAME, value='button'):
                    #     if btn.text == '요금바로 납부':
                    #         btn.click()
                    #         # time.sleep(3)
                    #
                    #         logging.info('요금 바로 납부 요청')
                    #         update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 요금바로 납부 요청')
                    #
                    #         found = True
                    #         break
                    #
                    # if not found:
                    #     raise Exception(self, '요금바로 납부 버튼 식별 실패')

                    break
                except Exception as e:
                    logging.info(e)
                    # time.sleep(0.5)
                    self.step -= 1
                    continue

            # 금액 확인
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    self.screenshot(message, chrome_driver, os.getcwd() + 'afterLogin-lgu.png')
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

            self.screenshot(message, chrome_driver, os.getcwd() + 'afterLogin-lgu.png')

            self.step += 1

            logging.info('금액 확인 완료')
            update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 금액 확인 완료')

        return charge_to_pay

    def login_lgu(self, message, chrome_driver, post_to_update):
        # 로그인 방법 선택 U+ID
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                self.screenshot(message, chrome_driver, os.getcwd() + 'afterLogin-lgu.png')
                return -1
            try:
                self.step += 1

                # found = False

                element = chrome_driver.find_element(By.XPATH, "// img[@alt='요금바로 납부']")
                element = element.find_element(By.XPATH, '..')
                element.click()

                logging.info('U+ID 로그인 선택')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] U+ID 로그인 선택')

                # for img in chrome_driver.find_elements(By.TAG_NAME, 'img'):
                #     if img.get_attribute('alt') == 'u+ID':
                #         loging_btn = img.find_element(By.XPATH, '..')
                #         loging_btn.click()
                #         found = True
                #         break
                #
                # if found:
                #     # time.sleep(3)
                #
                #     logging.info('U+ID 로그인 선택')
                #     update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] U+ID 로그인 선택')
                #
                #     break
                # else:
                #     logging.info('U+ID 로그인 찾기 실패')
                #     update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] U+ID 로그인 찾기 실패')
                #
                #     return -1

            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue

        # 로그인
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                self.screenshot(message, chrome_driver, os.getcwd() + 'afterLogin-lgu.png')
                return -1
            try:
                self.step += 1

                found = False

                # time.sleep(1)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'username-1-6'))
                self.waiter.until(condition).clear(condition)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'password-1'))
                self.waiter.until(condition).clear()

                # time.sleep(1)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'username-1-6'))
                self.waiter.until(condition).send_keys(self.id)

                condition = expected_conditions.visibility_of_element_located((By.ID, 'password-1'))
                self.waiter.until(condition).send_keys(self.password)

                for btn in chrome_driver.find_elements(by=By.TAG_NAME, value='button'):
                    if btn.text.replace(' ', '').replace('\n', '').replace('\r', '') == ('U+ID로그인'):
                        btn.click()

                        logging.info('로그인 시도중')
                        update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 로그인 시도중')

                        found = True

                        break
                if not found:
                    raise Exception(self, '로그인 버튼 식별 실패')

                break
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue

        # time.sleep(3)

    def screenshot(self, message, chrome_driver, path):
        with open(path, 'wb') as img:
            img.write(full_screenshot(chrome_driver))
            self.driver.reply_to(message, '', file_paths=[path])
            os.remove(path)
