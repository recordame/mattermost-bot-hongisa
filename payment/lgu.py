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


class LGU(Plugin):
    step = 1
    last_step = 8
    max_retry = 10

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
        #chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('disable-popup-blocking')

        chrome_options.add_experimental_option("detach", True)

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            self.step += 1

            logging.info('크롬 드라이브 호출')
            reply_msg = self.driver.reply_to(message, f'[{display_progress(self.step, self.last_step)}] 크롬 드라이브 호출')
            post_to_update = reply_msg['id']

            # 요금납부 페이지 호출
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    return -1

                try:
                    self.step += 1

                    logging.info('LG U+ 요금청구 페이지 호출')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] LG U+ 요금청구 페이지 호출')
                    chrome_driver.get(url)

                    break
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue

            # 로그인
            self.login_lgu(chrome_driver, post_to_update)

            # 요금바로 납부 선택
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    return -1
                try:
                    self.step += 1
                    found = False

                    time.sleep(3)

                    for btn in chrome_driver.find_elements(by=By.TAG_NAME, value='button'):
                        if btn.text == '요금바로 납부':
                            btn.click()
                            time.sleep(3)

                            logging.info('요금 바로 납부 요청')
                            update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 요금바로 납부 요청')

                            found = True
                            break
                    if not found:
                        print(chrome_driver.page_source)
                        raise Exception(self, '요금바로 납부 버튼 식별 실패')
                    break
                except Exception as e:
                    logging.info(e)
                    self.step -= 1
                    continue

            # 금액 확인
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    return -1

                try:
                    self.step += 1
                    try:

                        charge_to_pay = int(WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'pay-total-txt'))).text.replace('원', ''))
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

        return charge_to_pay

    def login_lgu(self, chrome_driver, post_to_update):
        # 로그인 방법 선택 U+ID
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                return -1

            try:
                self.step += 1
                found = False

                for img in chrome_driver.find_elements(by=By.TAG_NAME, value='img'):
                    if img.get_attribute('alt') == 'u+ID':
                        loging_btn = img.find_element(by=By.XPATH, value='..')
                        loging_btn.click()
                        found = True
                        break

                if found:
                    time.sleep(3)

                    logging.info('U+ID 로그인 선택')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] U+ID 로그인 선택')
                    break
                else:
                    logging.info('U+ID 로그인 찾기 실패')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] U+ID 로그인 찾기 실패')

                    return -1

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
                found = False

                time.sleep(1)

                WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'username-1-6'))).clear()
                WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'password-1'))).clear()

                WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'username-1-6'))).send_keys('recordame@naver.com')
                WebDriverWait(chrome_driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'password-1'))).send_keys('lkg0473PA!')

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
