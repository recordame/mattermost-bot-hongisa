# !/usr/bin/env python
import ssl

import urllib3
from mmpy_bot import Bot, Settings

from alarm.alarm_util import load_channel_alarms_from_file, load_user_alarms_from_file, load_ephemeral_alarms_from_file
from alarm.builtin.jinha import JinhaAlarm
from alarm.builtin.kordle import KordleAlarm
from alarm.builtin.mass import MassAlarm
from alarm.builtin.medicine import MedicineAlarm
from alarm.builtin.weather import WeatherAlarm
from alarm.command.alarm_list import AlarmList
from alarm.custom.channel_alarm import ChannelAlarm
from alarm.custom.ephemeral_alarm import EphemeralAlarm
from alarm.custom.user_alarm import UserAlarm
from command.currency import CurrencyAlarm
from command.help import Help
from command.simple import Simple
from command.todo import Todo
from common import constant
from webserver.controller import WebServer

urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

bot = Bot(
    settings=Settings(
        MATTERMOST_URL=constant.MATTERMOST_URL,
        MATTERMOST_PORT=constant.MATTERMOST_PORT,
        MATTERMOST_API_PATH='/api/v4',
        BOT_TOKEN=constant.BOT_TOKEN,
        BOT_TEAM=constant.BOT_TEAM,
        SSL_VERIFY=False,
        LOG_FILE='bot.log',
    ),
    plugins=[
        KordleAlarm(),
        MedicineAlarm(),
        WeatherAlarm(),
        MassAlarm(),
        JinhaAlarm(),
        Help(),
        CurrencyAlarm(),
        ChannelAlarm(),
        UserAlarm(),
        EphemeralAlarm(),
        AlarmList(),
        Todo(),
        Simple(),
        WebServer(),
    ],
)

# 로봇 설정
# 홍기사 스케쥴러 시작
constant.BACKGROUND_SCHEDULER.start()

# 할일 목록 알람 백그라운드 스케쥴 시작
constant.TODO_ALARM_SCHEDULER.start()

# 채널 알람을 위한 백그라운드 스케쥴 시작
constant.CHANNEL_ALARM_SCHEDULER.start()

# 사용자 정의 알람을 위한 백그라운드 스케쥴 시작
constant.USER_ALARM_SCHEDULER.start()

# 예약 메시지를 위한 백그라운드 스케쥴 시작
constant.EPHEMERAL_ALARM_SCHEDULER.start()

# 기동시 저장된 알람 복원
load_channel_alarms_from_file()
load_user_alarms_from_file()
load_ephemeral_alarms_from_file()

# 로봇 서비스 시작
bot.run()
