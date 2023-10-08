import json
import sys
from datetime import datetime, timedelta
from mmpy_bot import Message

from common import constant


def get_alarms(alarm_type: str, alarm_contexts: dict):
    msg: str = ''
    cnt: int = 0

    for channel_id in alarm_contexts.keys():
        alarms = alarm_contexts[channel_id].values()

        for alarm in alarms:
            cnt += 1
            msg += '[%s알람%d]\n' % (alarm_type, cnt) + alarm.get_info() + '\n'

    return '등록된 **%s**알람 : %d 개\n' % (alarm_type, cnt) + msg


def load_channel_alarms_from_file():
    recovery_mode: bool = True

    alarm_file = open('./alarms/channel_alarms.json', 'r', encoding='UTF-8')
    alarm_json = json.load(alarm_file)

    weather_alarm = getattr(sys.modules['alarm.builtin.weather'], 'WeatherAlarm')
    kordle_alarm = getattr(sys.modules['alarm.builtin.kordle'], 'KordleAlarm')
    mass_alarm = getattr(sys.modules['alarm.builtin.mass'], 'MassAlarm')
    medicine_alarm = getattr(sys.modules['alarm.builtin.medicine'], 'MedicineAlarm')
    jinha_alarm = getattr(sys.modules['alarm.builtin.jinha'], 'JinhaAlarm')
    random_alarm = getattr(sys.modules['alarm.builtin.random'], 'RandomAlarm')
    channel_alarm = getattr(sys.modules['alarm.custom.channel_alarm'], 'ChannelAlarm')

    for channel in alarm_json:
        for alarm in channel['alarm']:
            message_body: dict = {}

            message_body.update(
                {'data': {'post': {'user_id': alarm['creator_id']}, 'sender_name': alarm['creator_name'], }})
            message = Message(message_body)

            alarm_id = alarm.get('id')

            if alarm_id == 'weather':
                weather_alarm.add_alarm(
                    message,
                    alarm['message_argument'],
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
            elif alarm_id == 'random':
                random_alarm.add_alarm(
                    message,
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
                        recovery_mode,
                        alarm['job_status']
                    )
                else:
                    channel_alarm.add_alarm_cron(
                        message,
                        alarm['post_to'],
                        alarm['id'],
                        alarm['day'],
                        alarm['hour'],
                        alarm['minute'],
                        alarm['second'],
                        alarm['message'],
                        recovery_mode,
                        alarm['job_status']
                    )


def load_user_alarms_from_file():
    recovery_mode: bool = True

    alarm_file = open('./alarms/user_alarms.json', 'r', encoding='UTF-8')
    alarm_json = json.load(alarm_file)

    user_alarm = getattr(sys.modules['alarm.custom.user_alarm'], 'UserAlarm')

    for user in alarm_json:
        for alarm in user['alarm']:
            message_body: dict = {}

            message_body.update(
                {'data': {'post': {'user_id': alarm['creator_id']}, 'sender_name': alarm['creator_name']}})
            message = Message(message_body)

            if alarm['interval'] != '':
                user_alarm.add_alarm_interval(
                    message,
                    alarm['id'],
                    alarm['interval'],
                    alarm['interval_from'],
                    None,
                    alarm['message'],
                    recovery_mode,
                    alarm['job_status']
                )
            else:
                user_alarm.add_alarm_cron(
                    message,
                    alarm['id'],
                    alarm['day'],
                    alarm['hour'],
                    alarm['minute'],
                    alarm['second'],
                    alarm['message'],
                    recovery_mode,
                    alarm['job_status']
                )


def save_alarms_to_file_in_json(alarm_type: str, alarm_contexts: dict):
    _alarm_type = 'user' if alarm_type == '개인' else 'channel'

    alarm_file = open('./alarms/%s_alarms.json' % _alarm_type, 'w+', encoding='UTF-8')

    backup: list = []

    count = alarm_contexts.values().__len__()
    ids = list(alarm_contexts.keys())

    for i in range(0, count):
        _alarm_contexts: dict = alarm_contexts.get(ids[i])
        alarm_context_cnt = dict(_alarm_contexts).values().__len__()

        if alarm_context_cnt > 0:
            alarm_ids = list(dict(_alarm_contexts).keys())

            alarms: list = []

            for j in range(0, alarm_context_cnt):
                alarms.append((_alarm_contexts.get(alarm_ids[j])).get_dict())

            backup.append({_alarm_type: ids[i], 'alarm': alarms})

    json.dump(backup, alarm_file, indent=2, ensure_ascii=False)

    alarm_file.close()