import logging

from mmpy_bot import listen_to, Message, Plugin

from common import constant
from common.utils import get_today_str, read_json_file, write_json_file


class Todo(Plugin):
    user_todo_list: dict[str, list[str]] = {}

    def __init__(self):
        super().__init__()
        self.user_todo_list = load_todo_from_file()

        constant.TODO_ALARM_SCHEDULER.add_job(
            id='todo_notifier',
            func=lambda: self.notify_daily(self.user_todo_list),
            trigger='cron',
            day_of_week='*',
            hour='07',
            minute='00',
            misfire_grace_time=60
        )

    # 매일 아침 할일 목록 출력
    def notify_daily(self, user_todo_list: dict[str, list[str]]):
        for user_id in user_todo_list.keys():
            try:
                todo_list = self.user_todo_list[user_id]

                msg = f'`{get_today_str()}` 좋은 아침이에요 :sunny: 홍집사가 할일을 알려드릴게요!\n'
                msg += generate_todo_list(todo_list, user_id)

                self.driver.direct_message(user_id, msg)
            except KeyError:
                self.driver.direct_message(user_id, '할일이 없네요 :sunglasses:')

    @listen_to('^할일$')
    def show_todo(self, message: Message):
        logging.info('[stat] 할일목록')

        try:
            todo_list = self.user_todo_list[message.user_id]

            msg = generate_todo_list(todo_list, message.user_id)

            self.driver.direct_message(message.user_id, msg)
        except KeyError:
            self.driver.direct_message(message.user_id, '할일이 없네요 :sunglasses:')

    @listen_to('^\\+할일 (.+)$')
    def add_todo(self, message: Message, todo: str):
        logging.info('[stat] 할일등록')

        todo_list: list = []

        try:
            todo_list = self.user_todo_list[message.user_id]
        except KeyError:
            self.user_todo_list.update({message.user_id: []})

            todo_list = self.user_todo_list[message.user_id]
        finally:
            todo_list.append(todo)

            msg = generate_todo_list(todo_list, message.user_id)

            save_todo_to_file_in_json(self.user_todo_list)

            self.driver.direct_message(message.user_id, f'할일이 추가 되었어요 :fire:\n{msg}')

    @listen_to('^\\-할일 (\\d+)$')
    def done_todo(self, message: Message, todo_id: str):
        logging.info("[stat] 할일제거")

        try:
            todo_list = self.user_todo_list[message.user_id]

            if len(todo_list) == 0:
                self.driver.direct_message(message.user_id, '할일이 없네요 :sunglasses:')
            else:
                if int(todo_id) > len(todo_list):
                    self.driver.direct_message(message.user_id, '입력하신 숫자가 너무 커요 :crying_cat_face:')
                else:
                    del todo_list[int(todo_id) - 1]

                    if len(todo_list) == 0:
                        del self.user_todo_list[message.user_id]

                        self.driver.direct_message(message.user_id, '수고 하셨습니다! 모든 일을 끝내셨군요 :clap:')
                    else:
                        msg = generate_todo_list(todo_list, message.user_id)

                        self.driver.direct_message(message.user_id, f'수고 하셨습니다! 일 하나를 끝내셨군요 :clap:\n{msg}')

                    save_todo_to_file_in_json(self.user_todo_list)

        except KeyError:
            self.driver.direct_message(message.user_id, '할일이 없네요 :sunglasses:')


#########################

def generate_todo_list(todo_list: list, user_id: str):
    todo_id = 1
    msg = '**할일 목록**\n\n' \
          '|No.|할일|점검|\n' \
          '|---|---|---|\n'

    for todo in todo_list:
        msg += f'|{todo_id}|{todo}|[끝내기](http://{constant.FLASK_SERVER_IP}:{constant.FLASK_SERVER_PORT}/todo/{user_id}/{todo_id}/done)|\n'
        todo_id = todo_id + 1

    return msg


def load_todo_from_file():
    return dict(read_json_file('./json-db/todo.json'))


def save_todo_to_file_in_json(user_todo_list: dict):
    write_json_file('./json-db/todo.json', user_todo_list)
