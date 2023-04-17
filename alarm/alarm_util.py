import json
import sys

from mmpy_bot import Message


def get_alarms(alarm_type: str, alarm_contexts: dict):
    msg: str = ""
    cnt: int = 0

    for channel_id in alarm_contexts.keys():
        alarms = alarm_contexts[channel_id].values()

        for alarm in alarms:
            cnt += 1
            msg += "[%s알람%d]\n" % (alarm_type, cnt) + alarm.get_info() + "\n"

    return "등록된 **%s**알람 : %d 개\n" % (alarm_type, cnt) + msg


def load_user_alarms_from_file():
    recovery_mode: bool = True

    alarm_file = open("./alarms/user_alarms.json", "r", encoding="UTF-8")
    alarm_json = json.load(alarm_file)

    user_alarm = getattr(sys.modules["alarm.custom.user_alarm"], "UserAlarm")

    for user in alarm_json:
        for alarm in user["alarm"]:
            message_body: dict = {}

            message_body.update({"data": {"sender_name": alarm["creator_name"], "post": {"user_id": alarm["creator_id"]}}})
            message = Message(message_body)

            alarm_id = alarm["id"]
            day = alarm["day"]
            hour = alarm["hour"]
            minute = alarm["minute"]
            second = alarm["second"]
            alarm_message = alarm["message"]
            job_status = alarm["job_status"]

            user_alarm.add_alarm(
                message,
                alarm_id,
                day,
                hour,
                minute,
                second,
                alarm_message,
                recovery_mode,
                job_status
            )


def load_channel_alarms_from_file():
    recovery_mode: bool = True

    alarm_file = open("./alarms/channel_alarms.json", "r", encoding="UTF-8")
    alarm_json = json.load(alarm_file)

    weather_alarm = getattr(sys.modules["alarm.builtin.weather"], "WeatherAlarm")
    kordle_alarm = getattr(sys.modules["alarm.builtin.kordle"], "KordleAlarm")
    mass_alarm = getattr(sys.modules["alarm.builtin.mass"], "MassAlarm")
    medicine_alarm = getattr(sys.modules["alarm.builtin.medicine"], "MedicineAlarm")
    jinha_alarm = getattr(sys.modules["alarm.builtin.jinha"], "JinhaAlarm")
    channel_alarm = getattr(sys.modules["alarm.custom.channel_alarm"], "ChannelAlarm")

    for channel in alarm_json:
        for alarm in channel["alarm"]:
            message_body: dict = {}

            message_body.update({"data": {"sender_name": alarm["creator_name"], "post": {"user_id": alarm["creator_id"]}}})
            message = Message(message_body)

            alarm_id = alarm.get("id")

            if alarm_id == "weather":
                weather_alarm.add_alarm(
                    message,
                    alarm["message_argument"],
                    alarm["hour"],
                    alarm["minute"],
                    recovery_mode
                )
            elif alarm_id == "kordle":
                kordle_alarm.add_alarm(
                    message,
                    alarm["hour"],
                    alarm["minute"],
                    recovery_mode
                )
            elif alarm_id == "mass":
                mass_alarm.add_alarm(
                    message,
                    alarm["hour"],
                    alarm["minute"],
                    recovery_mode
                )
            elif alarm_id == "medicine":
                medicine_alarm.add_alarm(
                    message,
                    alarm["hour"],
                    alarm["minute"],
                    recovery_mode
                )
            elif alarm_id == "jinha":
                jinha_alarm.add_alarm(
                    message,
                    alarm["hour"],
                    alarm["minute"],
                    recovery_mode
                )
            else:
                channel_alarm.add_alarm(
                    message,
                    alarm["post_to"],
                    alarm["id"],
                    alarm["day"],
                    alarm["hour"],
                    alarm["minute"],
                    alarm["second"],
                    alarm["message"],
                    recovery_mode
                )


def save_alarms_to_file_in_json(alarm_type_user_or_channel: str, alarm_contexts_for_user_or_channel: dict):
    if alarm_type_user_or_channel == "개인":
        alarm_type = "user"
    else:
        alarm_type = "channel"

    alarm_file = open("./alarms/%s_alarms.json" % alarm_type, "w+", encoding="UTF-8")

    alarm_file.write("[")
    user_or_channel_cnt = alarm_contexts_for_user_or_channel.values().__len__()
    user_or_channel_ids = list(alarm_contexts_for_user_or_channel.keys())

    for i in range(0, user_or_channel_cnt):
        alarm_contexts: dict = alarm_contexts_for_user_or_channel.get(user_or_channel_ids[i])
        alarm_context_cnt = dict(alarm_contexts).values().__len__()

        if alarm_context_cnt > 0:
            alarm_file.write('{"%s":"%s", "alarm":[' % (alarm_type, user_or_channel_ids[i]))

            alarm_ids = list(dict(alarm_contexts).keys())

            for j in range(0, alarm_context_cnt):
                json.dump(
                    alarm_contexts.get(alarm_ids[j]).__dict__,
                    alarm_file,
                    indent=4,
                    ensure_ascii=False
                )

                if j < alarm_context_cnt - 1:
                    alarm_file.write(",\n")

            alarm_file.write("]}")

            if i < user_or_channel_cnt - 1:
                alarm_file.write(",\n")

    alarm_file.write("]")

    alarm_file.close()
