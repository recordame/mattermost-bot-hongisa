import json
import sys

from mmpy_bot import Message

from common import constant
from common.utils import create_mattermost_message_by_user_id_and_name, read_json_file


# 홍기사에 등록된 총 알람수 계산
def count_alarms(alarm_contexts: dict):
    count: int = 0

    for post_to in alarm_contexts.keys():
        alarms = alarm_contexts[post_to].values()

        count = count + len(alarms)

    return count


# 등록한 알람의 세부정보 출력
def get_alarm_info(alarm_type_kr: str, alarm_contexts: dict, channel_id: str = None, creator_id: str = None):
    message: str = ''
    index: int = 0

    if channel_id is None:
        for post_to in alarm_contexts.keys():
            alarms = alarm_contexts[post_to].values()

            for alarm in alarms:
                if creator_id == alarm.creator_id:
                    index += 1
                    message += f'[{alarm_type_kr}{index}]\n' \
                               f'{alarm.get_info()}\n' \
                               f'   - [취소하기](https://{constant.FLASK_SERVER_IP}/hongisa/alarm/{creator_id}/{alarm.post_to}/{alarm.id}/cancel)'

                    if alarm_type_kr == '개인':
                        if alarm.job_status == '실행':
                            message += f', [정지하기](https://{constant.FLASK_SERVER_IP}/hongisa/alarm/{creator_id}/{alarm.post_to}/{alarm.id}/pause)'
                        else:
                            message += f', [재개하기](https://{constant.FLASK_SERVER_IP}/hongisa/alarm/{creator_id}/{alarm.post_to}/{alarm.id}/resume)'

                    message += '\n'
    else:
        try:
            alarms = alarm_contexts[channel_id].values()

            for alarm in alarms:
                index += 1
                message += f'[{alarm_type_kr}{index}]\n' \
                           f'{alarm.get_info()}\n' \
                           f'   - [취소하기](https://{constant.FLASK_SERVER_IP}/hongisa/alarm/{creator_id}/{alarm.post_to}/{alarm.id}/cancel)\n'
        except KeyError:
            pass

    return f'등록 현황(**{alarm_type_kr}**): {index}개\n' \
           f'{message}'


# 개인 알람 파일로 부터 리로드
def reload_user_alarms_from_file():
    constant.USER_ALARMS.clear()
    constant.USER_ALARM_SCHEDULER.remove_all_jobs()

    load_user_alarms_from_file()


# 채널 알람 파일로 부터 리로드
def reload_channel_alarms_from_file():
    constant.CHANNEL_ALARMS.clear()
    constant.CHANNEL_ALARM_SCHEDULER.remove_all_jobs()

    load_channel_alarms_from_file()


# 메시지 예약 알람 파일로 부터 리로드
def reload_ephemeral_alarms_from_file():
    constant.EPHEMERAL_ALARMS.clear()
    constant.EPHEMERAL_ALARM_SCHEDULER.remove_all_jobs()

    load_ephemeral_alarms_from_file()


# 개인 알람 파일로 부터 로드
def load_user_alarms_from_file():
    recovery_mode: bool = True

    # circular import 문제로 클래스를 직접 탐색
    user_alarm = getattr(sys.modules['alarm.custom.user_alarm'], 'UserAlarm')

    alarm_json = read_json_file('./json-db/user_alarms.json')

    for user in alarm_json:
        for alarm in user['alarm']:
            message = create_mattermost_message_by_user_id_and_name(alarm['creator_id'], alarm['creator_name'])

            if alarm['interval'] != '':
                user_alarm.add_alarm_interval(
                    message,
                    alarm['id'],
                    alarm['interval'],
                    alarm['interval_from'],
                    None,  # 정규식 시작일중 시간영역을 위한 더미 변수
                    alarm['message'],
                    alarm['job_status'],
                    recovery_mode
                )
            else:
                user_alarm.add_alarm(
                    message,
                    alarm['id'],
                    alarm['day'],
                    alarm['hour'],
                    alarm['minute'],
                    alarm['second'],
                    alarm['message'],
                    alarm['job_status'],
                    recovery_mode
                )


# 채널 알람 파일로 부터 로드
def load_channel_alarms_from_file():
    recovery_mode: bool = True

    alarm_file = open('./json-db/channel_alarms.json', 'r', encoding='UTF-8')
    alarm_json = json.load(alarm_file)

    weather_alarm = getattr(sys.modules['alarm.builtin.weather'], 'WeatherAlarm')
    kordle_alarm = getattr(sys.modules['alarm.builtin.kordle'], 'KordleAlarm')
    mass_alarm = getattr(sys.modules['alarm.builtin.mass'], 'MassAlarm')
    medicine_alarm = getattr(sys.modules['alarm.builtin.medicine'], 'MedicineAlarm')
    jinha_alarm = getattr(sys.modules['alarm.builtin.jinha'], 'JinhaAlarm')
    channel_alarm = getattr(sys.modules['alarm.custom.channel_alarm'], 'ChannelAlarm')

    for channel in alarm_json:
        for alarm in channel['alarm']:
            message_body: dict = {}

            message_body.update({
                'data': {
                    'post': {
                        'user_id': alarm['creator_id']
                    },
                    'sender_name': alarm['creator_name']
                }
            })

            message = Message(message_body)

            alarm_id = alarm.get('id')

            if alarm_id == 'weather':
                location = alarm['message']
                weather_alarm.add_alarm(
                    message,
                    location,
                    alarm['hour'],
                    alarm['minute'],
                    recovery_mode
                )
            elif alarm_id == 'kordle':
                kordle_alarm.add_alarm(
                    message,
                    alarm['hour'],
                    alarm['minute'],
                    recovery_mode
                )
            elif alarm_id == 'mass':
                mass_alarm.add_alarm(
                    message,
                    alarm['hour'],
                    alarm['minute'],
                    recovery_mode
                )
            elif alarm_id == 'medicine':
                medicine_alarm.add_alarm(
                    message,
                    alarm['hour'],
                    alarm['minute'],
                    recovery_mode
                )
            elif alarm_id == 'jinha':
                jinha_alarm.add_alarm(
                    message,
                    alarm['hour'],
                    alarm['minute'],
                    recovery_mode
                )
            else:
                if alarm['interval'] != '':
                    channel_alarm.add_alarm_interval(
                        message,
                        alarm['post_to'],
                        alarm['id'],
                        alarm['interval'],
                        alarm['interval_from'],
                        None,
                        alarm['message'],
                        alarm['job_status'],
                        recovery_mode
                    )
                else:
                    channel_alarm.add_alarm(
                        message,
                        alarm['post_to'],
                        alarm['id'],
                        alarm['day'],
                        alarm['hour'],
                        alarm['minute'],
                        alarm['second'],
                        alarm['message'],
                        alarm['job_status'],
                        recovery_mode
                    )


# 메시지 예약 알람 파일로 부터 로드
def load_ephemeral_alarms_from_file():
    recovery_mode: bool = True

    # circular import 문제로 클래스를 직접 탐색
    ephemeral_alarm = getattr(sys.modules['alarm.custom.ephemeral_alarm'], 'EphemeralAlarm')

    alarm_json = read_json_file('./json-db/ephemeral_alarms.json')

    for ephemeral in alarm_json:
        for alarm in ephemeral['alarm']:
            message = create_mattermost_message_by_user_id_and_name(alarm['creator_id'], alarm['creator_name'])

            ephemeral_alarm.add_alarm(
                message,
                alarm['post_to'],
                alarm['id'],
                alarm['day'][0:4],
                alarm['day'][4:6],
                alarm['day'][6:8],
                alarm['hour'],
                alarm['minute'],
                alarm['second'],
                alarm['message'],
                alarm['job_status'],
                recovery_mode
            )


# 메모리 상에 저장된 알람을 파일에 json으로 내보내기
def save_alarms_to_file_in_json(alarm_type_kr: str, alarm_contexts: dict):
    alarm_type_en = ''

    if '개인' == alarm_type_kr:
        alarm_type_en = 'user'
    elif '채널' == alarm_type_kr:
        alarm_type_en = 'channel'
    elif '예약' == alarm_type_kr:
        alarm_type_en = 'ephemeral'

    if alarm_type_en != '':
        try:
            with open(f'./json-db/{alarm_type_en}_alarms.json', 'w+', encoding='UTF-8') as alarm_file:
                backup: list = []
                post_to_list = list(alarm_contexts.keys())

                for i in range(0, alarm_contexts.values().__len__()):
                    _alarm_contexts: dict = alarm_contexts.get(post_to_list[i])
                    alarm_context_cnt = dict(_alarm_contexts).values().__len__()

                    if alarm_context_cnt > 0:
                        alarm_ids = list(dict(_alarm_contexts).keys())

                        alarms: list = []

                        for j in range(0, alarm_context_cnt):
                            alarms.append((_alarm_contexts.get(alarm_ids[j])).get_dict())

                        backup.append(
                            {
                                alarm_type_en: post_to_list[i],
                                'alarm': alarms
                            }
                        )

                json.dump(backup, alarm_file, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            raise Exception(f'알람 파일({alarm_type_en}_alarms.json) 쓰기 실패')
