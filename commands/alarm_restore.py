import json
import sys

from mmpy_bot import Message, Plugin, listen_to

from commands.kordle import KordleAlarm
from commands.mass import MassAlarm
from commands.medicine import MedicineAlarm
from commands.my_alarm import MyAlarm
from commands.weather import WeatherAlarm
from commons.utils import (
    save_channel_alarms_to_file_in_json,
    save_personal_alarms_to_file_in_json,
)


def load_channel_alarms_from_file(message: Message):
    alarm_file = open("./channel_alarms.json", "r", encoding="UTF-8")
    alarm_json = json.load(alarm_file)

    weather_alarm: WeatherAlarm = getattr(sys.modules[__name__], "WeatherAlarm")
    kordle_alarm: KordleAlarm = getattr(sys.modules[__name__], "KordleAlarm")
    mass_alarm: MassAlarm = getattr(sys.modules[__name__], "MassAlarm")
    medicine_alarm: MedicineAlarm = getattr(sys.modules[__name__], "MedicineAlarm")

    for alarm in alarm_json:
        job_id = alarm.get("job_id")

        if job_id == "WeatherAlarm":
            weather_alarm.add_alarm(
                message,
                alarm.get("msg_param"),
                alarm.get("time").split(":")[0],
                alarm.get("time").split(":")[1],
            )
        elif job_id == "KordleAlarm":
            kordle_alarm.add_alarm(
                message,
                alarm.get("time").split(":")[0],
                alarm.get("time").split(":")[1],
            )
        elif job_id == "MassAlarm":
            mass_alarm.add_alarm(
                message,
                alarm.get("time").split(":")[0],
                alarm.get("time").split(":")[1],
            )
        elif job_id == "MedicineAlarm":
            medicine_alarm.add_alarm(
                message,
                alarm.get("time").split(":")[0],
                alarm.get("time").split(":")[1],
            )


def load_personal_alarms_from_file(message: Message):
    alarm_file = open("./personal_alarms.json", "r", encoding="UTF-8")
    alarm_json = json.load(alarm_file)

    my_alarm: MyAlarm = getattr(sys.modules[__name__], "MyAlarm")

    for user in alarm_json:
        for alarm in user["alarm"]:
            message.sender_name = alarm["creator"]
            message.user_id = alarm["creator_id"]
            label = alarm["alarm_name"]
            dow = alarm["day"]
            hour = str(alarm["time"]).split(":")[0]
            minute = str(alarm["time"]).split(":")[1]
            second = str(alarm["time"]).split(":")[2]
            msg = alarm["alarm_msg"]

            my_alarm.add_my_alarm(message, label, dow, hour, minute, second, msg)


class AlarmRestore(Plugin):
    @listen_to("^알람복원$")
    def load_channel_alarms(self, message: Message):
        load_channel_alarms_from_file(message)

    @listen_to("^알람저장$")
    def save_channel_alarms(self, message: Message):
        save_channel_alarms_to_file_in_json()
        self.driver.direct_message(message.user_id, "알람이 `channel_alarms`파일에 저장되었습니다.")

    @listen_to("^개인알람복원$")
    def load_personal_alarms(self, message: Message):
        load_personal_alarms_from_file(message)

    @listen_to("^개인알람저장$")
    def save_personal_alarms(self, message: Message):
        save_personal_alarms_to_file_in_json()
        self.driver.direct_message(message.user_id, "알람이 `personal_alarms`파일에 저장되었습니다.")
