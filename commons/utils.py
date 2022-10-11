import json


def get_alarms(alarm_ctxs: dict, post_to: str = ""):
    msg: str = ""
    cnt: int = 0

    if post_to == "":
        post_toes = alarm_ctxs.keys()

        for _post_to in post_toes:
            alarms = alarm_ctxs[_post_to].values()

            for alarm in alarms:
                cnt += 1
                msg += "[알람%d]\n" % cnt + alarm.get_info() + "\n"
    else:
        if alarm_ctxs.get(post_to) is not None:
            alarms = alarm_ctxs[post_to].values()

            for alarm in alarms:
                cnt += 1
                msg += "[알람%d]\n" % cnt + alarm.get_info() + "\n"

    return "등록된 알람 : %d 개\n" % cnt + msg


def save_alarms_to_file_in_json(alarm_type: str, alarm_ctxs: dict):
    alarm_file = open("./%s_alarms.json" % alarm_type, "w", encoding="UTF-8")

    alarm_file.write("[")
    ctx_cnt = alarm_ctxs.values().__len__()
    ctx_keys = list(alarm_ctxs.keys())

    for i in range(0, ctx_cnt):
        alarm_file.write('{"%s":"%s", "alarm":[' % (alarm_type, ctx_keys[i]))

        alarms: dict = alarm_ctxs.get(ctx_keys[i])
        alarm_cnt = dict(alarms).values().__len__()
        alarm_ids = list(dict(alarms).keys())

        for j in range(0, alarm_cnt):
            json.dump(
                alarms.get(alarm_ids[j]).__dict__,
                alarm_file,
                indent=4,
                ensure_ascii=False
            )

            if j < alarm_cnt - 1:
                alarm_file.write(",\n")

        alarm_file.write("]}")

        if i < ctx_cnt - 1:
            alarm_file.write(",\n")

    alarm_file.write("]")

    alarm_file.close()
