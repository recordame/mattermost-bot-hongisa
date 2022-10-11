import json
import sys

from mmpy_bot import Message, Plugin, listen_to

from commands.kordle import KordleAlarm
from commands.mass import MassAlarm
from commands.medicine import MedicineAlarm
from commands.user_alarm import UserAlarm
from commands.weather import WeatherAlarm
from commons import constants
from commons.utils import save_alarms_to_file_in_json


def load_channel_alarms_from_file(message: Message):
    alarm_file = open("./channel_alarms.json", "r", encoding="UTF-8")
    alarm_json = json.load(alarm_file)

    weather_alarm: WeatherAlarm = getattr(sys.modules[__name__], "WeatherAlarm")
    kordle_alarm: KordleAlarm = getattr(sys.modules[__name__], "KordleAlarm")
    mass_alarm: MassAlarm = getattr(sys.modules[__name__], "MassAlarm")
    medicine_alarm: MedicineAlarm = getattr(sys.modules[__name__], "MedicineAlarm")

    for channel in alarm_json:
        for alarm in channel["alarm"]:
            id = alarm.get("id")

            if id == "weather":
                weather_alarm.add_alarm(
                    message,
                    alarm["message_argument"],
                    alarm["hour"],
                    alarm["minute"],
                    alarm["post_to"]
                )
            elif id == "kordle":
                kordle_alarm.add_alarm(
                    message,
                    alarm["hour"],
                    alarm["minute"],
                    alarm["post_to"]
                )
            elif id == "mass":
                mass_alarm.add_alarm(
                    message,
                    alarm["hour"],
                    alarm["minute"],
                    alarm["post_to"]
                )
            elif id == "medicine":
                medicine_alarm.add_alarm(
                    message,
                    alarm["hour"],
                    alarm["minute"],
                    alarm["post_to"]
                )


def load_user_alarms_from_file(message: Message):
    alarm_file = open("./user_alarms.json", "r", encoding="UTF-8")
    alarm_json = json.load(alarm_file)

    user_alarm: UserAlarm = getattr(sys.modules[__name__], "UserAlarm")

    for user in alarm_json:
        for alarm in user["alarm"]:
            message.sender_name = alarm["creator_name"]
            message.user_id = alarm["creator_id"]

            alarm_id = alarm["id"]
            day = alarm["day"]
            hour = alarm["hour"]
            minute = alarm["minute"]
            second = alarm["second"]
            alarm_message = alarm["message"]

            user_alarm.add_user_alarm(
                message,
                alarm_id,
                day,
                hour,
                minute,
                second,
                alarm_message
            )


class AlarmRestore(Plugin):
    @listen_to("^채널알람복원$")
    def load_channel_alarms(self, message: Message):
        load_channel_alarms_from_file(message)

    @listen_to("^채널알람저장$")
    def save_channel_alarms(self, message: Message):
        save_alarms_to_file_in_json("channel", constants.CHANNEL_ALARMS)
        self.driver.direct_message(message.user_id, "알람이 `channel_alarms.json`파일에 저장되었습니다.")

    @listen_to("^개인알람복원$")
    def load_user_alarms(self, message: Message):
        load_user_alarms_from_file(message)

    @listen_to("^개인알람저장$")
    def save_user_alarms(self, message: Message):
        save_alarms_to_file_in_json("user", constants.USER_ALARMS)
        self.driver.direct_message(message.user_id, "알람이 `user_alarms.json`파일에 저장되었습니다.")
