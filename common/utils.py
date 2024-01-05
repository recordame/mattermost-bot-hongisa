import base64

import mmpy_bot
import urllib3
from selenium.webdriver.chrome.webdriver import WebDriver

urllib3.disable_warnings()


def update_post(driver: mmpy_bot.driver, post_id: str, new_message: str):
    req_data: dict = {
        'id': post_id,
        'message': new_message
    }

    driver.posts.update_post(post_id, options=req_data)


def display_progress(current_step, total_steps):
    progress_bar: str = ''

    for i in range(0, current_step):
        progress_bar += '■'

    for i in range(current_step, total_steps):
        progress_bar += '□'

    return progress_bar


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
