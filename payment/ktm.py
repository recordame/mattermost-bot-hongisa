import logging
import os
import time

import urllib3
from mmpy_bot import Plugin, listen_to, Message
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from common.utils import update_post, display_progress, full_screenshot

urllib3.disable_warnings()


class KTM(Plugin):
    max_retry = 10
    step = 1
    last_step = 6

    waiter: WebDriverWait

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

        with webdriver.Chrome(options=chrome_options) as chrome_driver:
            chrome_driver.implicitly_wait(10)

            self.waiter = WebDriverWait(chrome_driver, 10)
            self.step = 1
            self.last_step = 6

            logging.info('크롬 드라이브 호출')
            reply_msg = self.driver.reply_to(message, f'[{display_progress(self.step, self.last_step)}] 크롬 드라이브 호출')
            post_to_update = reply_msg['id']

            # 요금납부 페이지 호출
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
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
            self.login_ktm(chrome_driver, post_to_update)

            # 로그인 후 화면 스크린샷 전송 후 제거
            file = os.getcwd() + '/afterLogin-ktm.png'

            with open(file, 'wb') as img:
                img.write(full_screenshot(chrome_driver))
                self.driver.reply_to(message, '', file_paths=[file])
                os.remove(file)

            # 금액 확인
            for retry in range(self.max_retry):
                if retry == self.max_retry - 1:
                    return -1
                try:
                    self.step += 1

                    logging.info('금액 확인 중')
                    update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 금액 확인 중')

                    charge_to_pay = int(chrome_driver.find_element(By.ID, 'totalCntReal').get_attribute('value'))

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

    def login_ktm(self, chrome_driver, post_to_update):
        # 로그인
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                return -1

            try:
                self.step += 1

                chrome_driver.find_element(By.ID, 'userId').send_keys(self.id)
                chrome_driver.find_element(By.ID, 'passWord').send_keys(self.password)
                chrome_driver.find_element(By.ID, 'loginBtn').click()

                logging.info('로그인 시도중')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 로그인 시도중')

                time.sleep(3)

                break
            except Exception as e:
                logging.info(e)
                self.step -= 1
                continue

        try:
            chrome_driver.find_element(by=By.CLASS_NAME, value='c-button--w460').tag_name
        except:
            pass

        # SMS 인증을 요구 확인
        for retry in range(self.max_retry):
            if retry == self.max_retry - 1:
                return -1
            try:
                chrome_driver.find_element(By.CLASS_NAME, 'c-button--w460').click()

                self.last_step += 2
                self.step += 1

                logging.info('SMS 인증 요구 탐지')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] SMS 인증 요구 탐지')

                time.sleep(3)

                # SMS 인증 취소
                self.step += 1

                chrome_driver.find_element(By.ID, 'smsClosePopBtn').click()

                logging.info('SMS 인증 취소 중')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] SMS 인증 취소 중')

                time.sleep(3)

                # 재로그인 시도
                self.step += 1

                logging.info('재로그인 중')
                update_post(self.driver, post_to_update, f'[{display_progress(self.step, self.last_step)}] 재로그인 중')

                chrome_driver.find_element(By.ID, 'loginBtn').click()
            except:
                try:
                    chrome_driver.find_element(by=By.CLASS_NAME, value='c-button--w460').get_attribute('class')
                    continue
                except Exception as e:
                    logging.info(e)
                    break

        # 모든 단계 완료 후 잠시 대기
        time.sleep(3)
