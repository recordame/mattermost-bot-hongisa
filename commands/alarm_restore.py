import json
import sys

from mmpy_bot import Plugin, listen_to, Message

from commands.kordle import KordleAlarm
from commands.mass import MassAlarm
from commands.medicine import MedicineAlarm
from commands.weather import WeatherAlarm
from commons import constants


def load_file(message: Message):
    alarm_db = open('./alarms', 'r', encoding='UTF-8')
    alarms_from_db = json.load(alarm_db)

    weather_alarm: WeatherAlarm = getattr(sys.modules[__name__], "WeatherAlarm")
    kordle_alarm: KordleAlarm = getattr(sys.modules[__name__], "KordleAlarm")
    mass_alarm: MassAlarm = getattr(sys.modules[__name__], "MassAlarm")
    medicine_alarm: MedicineAlarm = getattr(sys.modules[__name__], "MedicineAlarm")

    for alarm in alarms_from_db:
        job_id = alarm.get('job_id')

        if job_id == 'WeatherAlarm':
            weather_alarm.add_alarm(message,
                                    alarm.get('msg_param'),
                                    alarm.get('time').split(':')[0],
                                    alarm.get('time').split(':')[1])
        elif job_id == 'KordleAlarm':
            kordle_alarm.add_alarm(message,
                                   alarm.get('time').split(':')[0],
                                   alarm.get('time').split(':')[1])
        elif job_id == 'MassAlarm':
            mass_alarm.add_alarm(message,
                                 alarm.get('time').split(':')[0],
                                 alarm.get('time').split(':')[1])
        elif job_id == 'MedicineAlarm':
            medicine_alarm.add_alarm(message,
                                     alarm.get('time').split(':')[0],
                                     alarm.get('time').split(':')[1])


def save_file():
    # 알림정보 파일 저장
    alarm_db = open('./alarms', 'w', encoding='UTF-8')

    alarm_db.write('[')

    i = 0
    cnt = constants.ALARMS.values().__len__()
    key = list(constants.ALARMS.keys())

    while i < cnt:
        json.dump(constants.ALARMS.get(key[i]).__dict__, alarm_db, indent=4, ensure_ascii=False)

        i += 1

        if i < cnt:
            alarm_db.write(',\n')

    alarm_db.write(']')
    alarm_db.close()


class AlarmRestore(Plugin):
    @listen_to('^알림복원$')
    def load_alarms(self, message: Message):
        load_file(message)

    @listen_to('^알림저장$')
    def save_alarms(self, message: Message):
        save_file()
        self.driver.direct_message(message.user_id, '알림이 `alarms`파일에 저장되었습니다.')
