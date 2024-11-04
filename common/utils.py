import base64
import json
import logging
import os
from datetime import timedelta, datetime

import requests
from mmpy_bot.driver import Driver, Message
from selenium.webdriver.chrome.webdriver import WebDriver

from common import constant
from common.constant import KR_TIME_ZONE


def display_progress(current_step, total_steps):
    progress_bar: str = ''

    for i in range(0, current_step):
        progress_bar += '■'

    for i in range(current_step, total_steps):
        progress_bar += '□'

    return progress_bar


def screenshot(driver: Driver, message: Message, chrome_driver: WebDriver, path: str):
    with open(path, 'wb') as img:
        img.write(full_screenshot(chrome_driver))
        driver.reply_to(message, '', file_paths=[path])

    os.remove(path)


def full_screenshot(chrome_driver: WebDriver) -> bytes:
    metrics = chrome_driver.execute_cdp_cmd('Page.getLayoutMetrics', {})

    return base64.b64decode(chrome_driver.execute_cdp_cmd('Page.captureScreenshot', {
        'clip': {
            'x': 0,
            'y': 0,
            'width': metrics['contentSize']['width'],
            'height': metrics['contentSize']['height'],
            'scale': 1
        },
        'captureBeyondViewport': True
    })['data'])


# 오늘 일자 정보 텍스트 생성
def get_today_str():
    day = ['월', '화', '수', '목', '금', '토', '일']

    now = datetime.now(tz=KR_TIME_ZONE)
    today = f'{now.strftime("%Y")}. {int(now.strftime("%m"))}. {int(now.strftime("%d"))}.({day[now.weekday()]})'

    return today


# 오늘이 속한 주의 월요일 날짜 계산
def get_date_of_monday_in_this_week(now):
    today = datetime(now.year, now.month, now.day)
    days_to_monday = today.weekday()

    return now + timedelta(days=-days_to_monday)


# 해당 일이 속한 달의 다음달 계산
def get_next_month(date):
    if date.month == 12:
        return datetime(date.year + 1, 1, 1, tzinfo=KR_TIME_ZONE)
    else:
        return datetime(date.year, date.month + 1, 1, tzinfo=KR_TIME_ZONE)


# 해당 일이 속한 달의 첫 번째 월요일 계산
def get_first_monday(date):
    offset = 0 - date.weekday()  # weekday = 0 means monday

    if offset < 0:
        offset += 7

    return date + timedelta(offset)


# 해당 일이 속한 날의 2주 전 날짜 계산
def get_two_weeks_before(date):
    return date + timedelta(-14)


# 사용자 아이디와 사용자 명만 담은 메터모스트 메시지 이벤트 객체 반환
def create_mattermost_message_by_user_id_and_name(user_id: str, user_name: str) -> Message:
    message_body: dict = {}
    message_body.update(
        {
            'data': {
                'post': {
                    'user_id': user_id
                },
                'sender_name': user_name,
                'channel_type': 'D',
            }
        }
    )

    return Message(message_body)


# 메터모스트 채널 아이디로 채널 정보 획득
def get_info_by_id(info: str, info_id: str) -> dict:
    try:
        with requests.session() as session:
            url = f'{constant.MATTERMOST_URL}:{constant.MATTERMOST_PORT}/api/v4/{info}/{info_id}'

            session.headers = {
                'authorization': 'Bearer ' + constant.BOT_TOKEN
            }

            response = session.get(url=url, verify=False)

            if response.status_code != 200:
                raise Exception('메터모스트 오류 응답')

            return response.json()
    except:
        logging.error(f'메터모스트 API(/api/v4/{info}/{info_id})를 통해 정보를 가져오는 중 실패')

        return {}


# 홍기사와 1:1 대화방인지, 채널에서 요청인지 확인하여 응답 전달
def send_or_post_message(driver: Driver, message: Message, msg: str):
    if message.body['data']['channel_name'] == constant.BOT_ID + '__' + message.user_id:
        driver.direct_message(message.user_id, msg)
    else:
        driver.create_post(message.channel_id, msg)


# json 파일을 읽어서 객체 반환
def read_json_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='UTF-8') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        logging.error(f'파일({file_path}) 읽기 실패')


# json 객체을 읽어서 파일 생성
def write_json_file(file_path: str, json_to_write):
    with open(file_path, 'w+', encoding='UTF-8') as json_file:
        json.dump(
            json_to_write,
            json_file,
            indent=2,
            ensure_ascii=False
        )


def rewrite_flex_work_session_info(key, value):
    constant_path = './common/constant.py'

    edited_lines = []

    with open(constant_path, encoding='UTF-8') as f:
        lines = f.readlines()
        for line in lines:
            if key in line:
                edited_lines.append(f"{key} = '{value}'\n")
            else:
                edited_lines.append(line)

    with open(constant_path, 'w', encoding='UTF-8') as f:
        f.writelines(edited_lines)
