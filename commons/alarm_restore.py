import json
import sys

from mmpy_bot import Plugin, listen_to, Message

from commands.kordle import KordleAlarm
from commands.mass import MassAlarm
from commands.medicine import MedicineAlarm
from commands.weather import WeatherAlarm


def load_from_file(message: Message):
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


class AlarmRestore(Plugin):
    @listen_to('^알림복원$')
    def load_alarms(self, message: Message):
        load_from_file(message)
