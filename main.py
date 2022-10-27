# !/usr/bin/env python

from mmpy_bot import Bot, Settings

from common import constant
from alarm.builtin.kordle import KordleAlarm
from alarm.builtin.mass import MassAlarm
from alarm.builtin.medicine import MedicineAlarm
from alarm.builtin.weather import WeatherAlarm
from alarm.custom.user_alarm import UserAlarm
from alarm.management.alarm_restore import AlarmRestore
from alarm.management.alarms import Alarms
from command.currency import CurrencyAlarm
from command.help import Help

# 로봇 설정
bot = Bot(
    settings=Settings(
        MATTERMOST_URL=constant.MATTERMOST_URL,
        MATTERMOST_PORT=443,
        MATTERMOST_API_PATH="/api/v4",
        BOT_TOKEN=constant.BOT_TOKEN,
        BOT_TEAM=constant.BOT_TEAM,
        SSL_VERIFY=False,
        LOG_FILE="./bot.log",
    ),
    plugins=[
        KordleAlarm(),
        MedicineAlarm(),
        WeatherAlarm(),
        MassAlarm(),
        Help(),
        Alarms(),
        CurrencyAlarm(),
        UserAlarm(),
        AlarmRestore()
    ],
)

# 알람을 위한 백그라운드 스케쥴 시작
constant.CHANNEL_ALARM_SCHEDULE.start()

# 사용자 정의 알람을 위한 백그라운드 스케쥴 시작
constant.USER_ALARM_SCHEDULE.start()

# 로봇 서비스 시작
bot.run()
