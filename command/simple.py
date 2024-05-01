import logging

from mmpy_bot import Plugin, Message, listen_to

from common.utils import get_today_str


class Simple(Plugin):
    @listen_to('^오늘$')
    def return_today(self, message: Message):
        logging.info("[stat] 오늘날짜")

        self.driver.direct_message(message.user_id, get_today_str())
