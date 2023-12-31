import logging
import time

import urllib3
from mmpy_bot import Plugin, listen_to, Message
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from common.utils import update_post, display_progress

urllib3.disable_warnings()


class LGU(Plugin):
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

            logging.info('크롬 드라이브 호출')
            self.driver.reply_to(message, f'[{display_progress(step, last_step)}] 크롬 드라이브 호출')
            post_to_update = self.driver.get_thread(message.id)['order'][1]

            # 요금납부 페이지 호출
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1

                    logging.info('LG U+ 요금청구 페이지 호출')
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] LG U+ 요금청구 페이지 호출')
                    chrome_driver.get(url)

                    break
                except Exception as e:
                    logging.info(e)

                    step -= 1
                    continue

            # 로그인 방법 선택 U+ID
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1

                    chrome_driver.find_element(by=By.ID, value='_uid_236').click()
                    logging.info('U+ID 로그인 선택')
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] U+ID 로그인 선택')

                    break
                except Exception as e:
                    logging.info(e)

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

                            logging.info('로그인 시도중')
                            update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 로그인 시도중')

                            time.sleep(3)

                            found = True
                            break
                    if not found:
                        raise BaseException('로그인 버튼 식별 실패')

                    break
                except Exception as e:
                    logging.info(e)

                    step -= 1
                    time.sleep(0.5)
                    continue

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

                            logging.info('요금 바로 납부 요청')
                            update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 요금 바로 납부 요청')

                            found = True
                            break
                    if not found:
                        raise BaseException('요금바로 납부 버튼 식별 실패')

                    break
                except Exception as e:
                    logging.info(e)

                    step -= 1
                    time.sleep(0.5)
                    continue

            # 금액 확인
            time.sleep(2)
            for retry in range(max_retry):
                if retry == max_retry - 1:
                    return -1

                try:
                    step += 1
                    try:
                        charge_to_pay = int(chrome_driver.find_element(by=By.CLASS_NAME, value='pay-total-txt').text.replace('원', ''))
                    except ValueError:
                        charge_to_pay = 0

                    logging.info('금액 확인 중')
                    update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 금액 확인 중')

                    if charge_to_pay > 0:
                        pass
                    else:
                        pass

                    break
                except Exception as e:
                    logging.info(e)

                    step -= 1
                    time.sleep(0.5)
                    continue

            step += 1

            logging.info('금액 확인 완료')
            update_post(self.driver, post_to_update, f'[{display_progress(step, last_step)}] 금액 확인 완료')

        return charge_to_pay
