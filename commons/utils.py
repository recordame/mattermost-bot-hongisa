import json

from commons import constants


def save_channel_alarms_to_file_in_json():
    # 알람정보 파일 저장
    alarm_db = open("./channel_alarms.json", "w", encoding="UTF-8")

    alarm_db.write("[")
    cnt = constants.ALARMS.values().__len__()
    key = list(constants.ALARMS.keys())

    for i in range(0, cnt):
        json.dump(
            constants.ALARMS.get(key[i]).__dict__,
            alarm_db,
            indent=4,
            ensure_ascii=False,
        )

        if i < cnt - 1:
            alarm_db.write(",\n")

    alarm_db.write("]")
    alarm_db.close()


def save_personal_alarms_to_file_in_json():
    # 알람정보 파일 저장
    alarm_file = open("./personal_alarms.json", "w", encoding="UTF-8")

    alarm_file.write("[")
    user_cnt = constants.MY_ALARMS.values().__len__()
    user_ids = list(constants.MY_ALARMS.keys())

    for i in range(0, user_cnt):
        alarms = constants.MY_ALARMS.get(user_ids[i])

        alarm_file.write('{"name":"' + user_ids[i] + '", "alarm":[')

        alarm_cnt = dict(alarms).values().__len__()
        alarm_ids = list(dict(alarms).keys())

        for j in range(0, alarm_cnt):
            json.dump(
                dict(alarms).get(alarm_ids[j]).__dict__,
                alarm_file,
                indent=4,
                ensure_ascii=False,
            )

            if j < alarm_cnt - 1:
                alarm_file.write(",\n")

        if i < user_cnt - 1:
            alarm_file.write(",\n")

        alarm_file.write("]}")

    alarm_file.write("]")
    alarm_file.close()
