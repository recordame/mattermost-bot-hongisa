import logging
import threading

import mattermostdriver
import mmpy_bot.driver
from flask import Flask, render_template, request, redirect
from mmpy_bot import listen_to, Message, Plugin

from alarm.builtin.jinha import JinhaAlarm
from alarm.builtin.kordle import KordleAlarm
from alarm.builtin.mass import MassAlarm
from alarm.builtin.medicine import MedicineAlarm
from alarm.builtin.weather import WeatherAlarm
from alarm.custom.channel_alarm import ChannelAlarm
from alarm.custom.ephemeral_alarm import EphemeralAlarm
from alarm.custom.user_alarm import UserAlarm
from command.todo import Todo
from common import constant
from common.utils import create_mattermost_message_by_user_id_and_name, get_info_by_id

# 웹 서버 기동

app = Flask(__name__)
threading.Thread(daemon=True, target=app.run, kwargs={'host': '0.0.0.0', 'port': constant.FLASK_SERVER_PORT}).start()


# 알람 등록 용 웹 페이지 호출
@app.route("/<user_id>/<user_name>", methods=['GET'])
def display_index(user_id: str, user_name: str):
    logging.info(f'[Web] 입장')

    return render_template('index.html', user_id=user_id, user_name=user_name)


# 알람 등록 후, 처음으로 돌아가기
@app.route("/result", methods=['POST'])
def process_command_and_redirect_to_index():
    error_page = f'<!DOCTYPE HTML>' \
                 f'<html>' \
                 f'문제가 발생했어요.. 홍집사아빠를 찾아 주세요!' \
                 f'</html>'

    inputs = request.form

    try:
        register_alarm(inputs)

        return redirect(f'/{inputs.get("사용자 ID")}/{inputs.get("사용자 명")}')
    except:
        return error_page


# 사다리타기 호출
@app.route("/ladder-game", methods=['GET'])
def ladder_game():
    return render_template('ladder_game.html')


# 할일 끝내기 호출
@app.route("/todo/<user_id>/<todo_id>/done", methods=['GET'])
def delete_todo(user_id: str, todo_id: str):
    message = create_mattermost_message_by_user_id_and_name(user_id, '')

    try:
        Todo.done_todo(message, todo_id)
        return '할일 삭제 완료! 창을 닫아주세요! ', 200
    except:
        return '오류가 발생했어요ㅠ 홍집사 주인에게 문의해 주세요!', 500


# 알람 등록 처리
def register_alarm(inputs: dict):
    logging.info(f'[Web] {inputs}')

    message = create_mattermost_message_by_user_id_and_name(inputs.get('사용자 ID'), inputs.get('사용자 명'))

    alarm_type = inputs.get('type')
    alarm_category = inputs.get('alarm')

    if alarm_type == '채널알람':
        if alarm_category == '날씨':
            WeatherAlarm.add_alarm(
                message,
                inputs.get('메시지'),
                inputs.get('시'),
                inputs.get('분'),
            )
        elif alarm_category == '꼬들':
            KordleAlarm.add_alarm(
                message,
                inputs.get('시'),
                inputs.get('분')
            )
        elif alarm_category == '미사':
            MassAlarm.add_alarm(
                message,
                inputs.get('시'),
                inputs.get('분')
            )
        elif alarm_category == '복약':
            MedicineAlarm.add_alarm(
                message,
                inputs.get('시'),
                inputs.get('분')
            )
        elif alarm_category == '진하':
            JinhaAlarm.add_alarm(
                message,
                inputs.get('시'),
                inputs.get('분')
            )
        elif alarm_category == '특정 일자 반복':
            ChannelAlarm.add_alarm(
                message,
                inputs.get('채널 ID'),
                inputs.get('알람명'),
                inputs.get('일자'),
                inputs.get('시'),
                inputs.get('분'),
                inputs.get('초'),
                inputs.get('메시지')
            )
        elif alarm_category == '특정 주기 반복':
            ChannelAlarm.add_alarm_interval(
                message,
                inputs.get('채널 ID'),
                inputs.get('알람명'),
                inputs.get('주기'),
                inputs.get('기준 시점'),
                None,
                inputs.get('메시지')
            )
        elif alarm_category == '1회 예약 발송':
            EphemeralAlarm.add_alarm(
                message,
                inputs.get('채널 ID'),
                inputs.get('예약명'),
                inputs.get('년'),
                inputs.get('월'),
                inputs.get('일'),
                inputs.get('시'),
                inputs.get('분'),
                inputs.get('초'),
                inputs.get('메시지')
            )
    elif alarm_type == '개인알람':
        if alarm_category == '특정 일자 반복':
            UserAlarm.add_alarm(
                message,
                inputs.get('알람명'),
                inputs.get('일자'),
                inputs.get('시'),
                inputs.get('분'),
                inputs.get('초'),
                inputs.get('메시지')
            )
        elif alarm_category == '특정 주기 반복':
            UserAlarm.add_alarm_interval(
                message,
                inputs.get('알람명'),
                inputs.get('주기'),
                inputs.get('기준 시점'),
                None,
                inputs.get('메시지')
            )
        elif alarm_category == '1회 예약 발송':
            EphemeralAlarm.add_user_alarm(
                message,
                inputs.get('예약명'),
                inputs.get('년'),
                inputs.get('월'),
                inputs.get('일'),
                inputs.get('시'),
                inputs.get('분'),
                inputs.get('초'),
                inputs.get('메시지')
            )


# 알람 취소 처리
@app.route("/alarm/<user_id>/<destination_id>/<alarm_id>/cancel", methods=['GET'])
def cancel_alarm(user_id: str, destination_id: str, alarm_id: str):
    user = get_info_by_id('users', user_id)
    message = create_mattermost_message_by_user_id_and_name(user_id, user['username'])

    is_processed: bool = False

    # 사용자 아이디와 알람 전달 목적지가 다른 경우 채널알람에서 탐색
    if user_id != destination_id:
        try:
            for alarm in constant.CHANNEL_ALARMS.get(destination_id).values():
                if (alarm.id == alarm_id) & (alarm_id == 'jinha'):
                    JinhaAlarm.cancel_alarm(message, destination_id)
                    is_processed = True
                    break

                elif (alarm.id == alarm_id) & (alarm_id == 'kordle'):
                    KordleAlarm.cancel_alarm(message, destination_id)
                    is_processed = True
                    break

                elif (alarm.id == alarm_id) & (alarm_id == 'mass'):
                    MassAlarm.cancel_alarm(message, destination_id)
                    is_processed = True
                    break

                elif (alarm.id == alarm_id) & (alarm_id == 'medicine'):
                    MedicineAlarm.cancel_alarm(message, destination_id)
                    is_processed = True
                    break

                elif (alarm.id == alarm_id) & (alarm_id == 'weather'):
                    WeatherAlarm.cancel_alarm(message, destination_id)
                    is_processed = True
                    break

                else:
                    ChannelAlarm.cancel_alarm(message, destination_id, alarm_id)
                    is_processed = True
                    break
        except:
            for alarm in constant.EPHEMERAL_ALARMS.get(destination_id).values():
                if alarm.id == alarm_id:
                    EphemeralAlarm.cancel_alarm(message, destination_id, alarm_id)
                    is_processed = True
                    break

    # 사용자 아이디와 알람 전달 목적지가 같은 경우 개인알람에서 탐색
    else:
        try:
            for alarm in constant.USER_ALARMS.get(destination_id).values():
                if alarm.id == alarm_id:
                    UserAlarm.cancel_alarm(message, alarm_id)
                    is_processed = True
                    break
        except:
            for alarm in constant.EPHEMERAL_ALARMS.get(destination_id).values():
                if alarm.id == alarm_id:
                    EphemeralAlarm.cancel_user_alarm(message, alarm_id)
                    is_processed = True
                    break

    # 결과 출력
    if is_processed:
        return f'홍집사에게 삭제 요청 전달 완료! 홍집사와 대화창에서 결과를 확인해 보세요!<br/>' \
               f'- 채널/유저 ID: {destination_id}<br/>' \
               f'- 삭제 요청 항목: {alarm_id}<br/><br/>' \
               f'<a href="http://{constant.FLASK_SERVER_IP}:{constant.FLASK_SERVER_PORT}/' \
               f'{message.user_id}/' \
               f'{message.sender_name}">신규알람 등록하기</a>', 200
    else:
        return f'오류가 발생했어요ㅠ 홍집사아빠에게 문의해 주세요!<br>' \
               f'- 채널/유저 ID: {destination_id}<br/>' \
               f'- 삭제 요청 항목: {alarm_id}', 500


# 개인 알람 정지 처리
@app.route("/alarm/<user_id>/<destination_id>/<alarm_id>/pause", methods=['GET'])
def pause_user_alarm(user_id: str, destination_id: str, alarm_id: str):
    user = get_info_by_id('users', user_id)
    message = create_mattermost_message_by_user_id_and_name(user_id, user['username'])

    is_processed: bool = False

    try:
        for alarm in constant.USER_ALARMS.get(destination_id).values():
            if alarm.id == alarm_id:
                UserAlarm.pause_alarm(message, alarm_id)
                is_processed = True
                break
    except:
        pass

    # 결과 출력
    if is_processed:
        return f'홍집사에게 정지 요청 전달 완료! 홍집사와 대화창에서 결과를 확인해 보세요!<br/>' \
               f'- 유저 ID: {destination_id}<br/>' \
               f'- 정지 요청 항목: {alarm_id}<br/><br/><br/>', 200
    else:
        return f'오류가 발생했어요ㅠ 홍집사아빠에게 문의해 주세요!<br>' \
               f'- 유저 ID: {destination_id}<br/>' \
               f'- 정지 요청 항목: {alarm_id}', 500


# 개인 알람 재개 처리
@app.route("/alarm/<user_id>/<destination_id>/<alarm_id>/resume", methods=['GET'])
def resume_user_alarm(user_id: str, destination_id: str, alarm_id: str):
    user = get_info_by_id('users', user_id)
    message = create_mattermost_message_by_user_id_and_name(user_id, user['username'])

    is_processed = False

    try:
        for alarm in constant.USER_ALARMS.get(destination_id).values():
            if alarm.id == alarm_id:
                UserAlarm.resume_alarm(message, alarm_id)
                is_processed = True
                break
    except:
        pass

    # 결과 출력
    if is_processed:
        return f'홍집사에게 재개 요청 전달 완료! 홍집사와 대화창에서 결과를 확인해 보세요!<br/>' \
               f'- 유저 ID: {destination_id}<br/>' \
               f'- 재개 요청 항목: {alarm_id}<br/><br/><br/>', 200
    else:
        return f'오류가 발생했어요ㅠ 홍집사아빠에게 문의해 주세요!<br>' \
               f'- 유저 ID: {destination_id}<br/>' \
               f'- 재개 요청 항목: {alarm_id}', 500


class WebServer(Plugin):
    @listen_to("^홍집사$")
    def create_command_api_url(self, message: Message):
        self.driver.direct_message(message.user_id, f'[홍집사:coffee:]('
                                                    f'http://{constant.FLASK_SERVER_IP}:{constant.FLASK_SERVER_PORT}/'
                                                    f'{message.user_id}/'
                                                    f'{message.sender_name}'
                                                    f') 입장하기!'
                                   )

    @listen_to("^사다리게임$")
    def post_ladder_game_url(self, message: Message):
        self.driver.direct_message(message.user_id, f'[사다리 게임]('
                                                    f'http://{constant.FLASK_SERVER_IP}:{constant.FLASK_SERVER_PORT}/ladder-game'
                                                    f') 입장하기!'
                                   )
