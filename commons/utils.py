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
                msg += "[채널알람%d]\n" % cnt + alarm.get_info() + "\n"

        return "등록된 **채널**알람 : %d 개\n" % cnt + msg
    else:
        if post_to == "ALL":
            for user in alarm_ctxs.keys():
                alarms = alarm_ctxs[user].values()

                for alarm in alarms:
                    cnt += 1
                    msg += "[개인알람%d]\n" % cnt + alarm.get_info() + "\n"

            return "등록된 **개인**알람 : %d 개\n" % cnt + msg
        else:
            if alarm_ctxs.get(post_to) is not None:
                alarms = alarm_ctxs[post_to].values()

                for alarm in alarms:
                    cnt += 1
                    msg += "[개인알람%d]\n" % cnt + alarm.get_info() + "\n"

                return "등록된 **개인**알람 : %d 개\n" % cnt + msg


def save_alarms_to_file_in_json(alarm_type: str, alarm_ctxs: dict):
    alarm_file = open("./alarms/%s_alarms.json" % alarm_type, "w", encoding="UTF-8")

    alarm_file.write("[")
    ctx_cnt = alarm_ctxs.values().__len__()
    ctx_keys = list(alarm_ctxs.keys())

    for i in range(0, ctx_cnt):
        alarms: dict = alarm_ctxs.get(ctx_keys[i])
        alarm_cnt = dict(alarms).values().__len__()

        if alarm_cnt > 0:
            alarm_file.write('{"%s":"%s", "alarm":[' % (alarm_type, ctx_keys[i]))

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

# def get_hwp_text(filename):
#     f = olefile.OleFileIO(filename)
#     dirs = f.listdir()
#
#     # HWP 파일 검증
#     if ["FileHeader"] not in dirs or ["\x05HwpSummaryInformation"] not in dirs:
#         raise Exception("Not Valid HWP.")
#
#     # 문서 포맷 압축 여부 확인
#     header = f.openstream("FileHeader")
#     header_data = header.read()
#     is_compressed = (header_data[36] & 1) == 1
#
#     # Body Sections 불러오기
#     nums = []
#     for d in dirs:
#         if d[0] == "BodyText":
#             nums.append(int(d[1][len("Section"):]))
#
#     sections = ["BodyText/Section" + str(x) for x in sorted(nums)]
#
#     # 전체 text 추출
#     text = ""
#     for section in sections:
#         bodytext = f.openstream(section)
#         data = bodytext.read()
#         if is_compressed:
#             unpacked_data = zlib.decompress(data, -15)
#         else:
#             unpacked_data = data
#
#         # 각 Section 내 text 추출
#         section_text = ""
#         i = 0
#         size = len(unpacked_data)
#         while i < size:
#             header = struct.unpack_from("<I", unpacked_data, i)[0]
#             rec_type = header & 0x3ff
#             rec_len = (header >> 20) & 0xfff
#
#             if rec_type in [67]:
#                 rec_data = unpacked_data[i + 4:i + 4 + rec_len]
#                 section_text += rec_data.decode('utf-16')
#                 section_text += "\n"
#
#             i += 4 + rec_len
#
#         text += section_text
#         text += "\n"
#
#     f.close()
#
#     return text
