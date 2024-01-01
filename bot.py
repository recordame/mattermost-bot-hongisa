# !/usr/bin/env python
import ssl

import urllib3
from mmpy_bot import Bot, Settings

from alarm.alarm_util import load_channel_alarms_from_file, load_user_alarms_from_file
from alarm.builtin.jinha import JinhaAlarm
from alarm.builtin.kordle import KordleAlarm
from alarm.builtin.mass import MassAlarm
from alarm.builtin.medicine import MedicineAlarm
from alarm.builtin.weather import WeatherAlarm
from alarm.command.alarm_list import Alarms
from alarm.custom.channel_alarm import ChannelAlarm
from alarm.custom.user_alarm import UserAlarm
from command.currency import CurrencyAlarm
from command.help import Help
from common import constant
from payment.ktm import KTM
from payment.lgu import LGU
from payment.liivm import LiivM

urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

# 로봇 설정
bot = Bot(
    settings=Settings(
        MATTERMOST_URL=constant.MATTERMOST_URL,
        MATTERMOST_PORT=8065,
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
        Help(),
        Alarms(),
        CurrencyAlarm(),
        ChannelAlarm(),
        UserAlarm(),
        JinhaAlarm(),
        LiivM(),
        KTM(),
        LGU()
    ],
)

# 알람을 위한 백그라운드 스케쥴 시작
constant.CHANNEL_ALARM_SCHEDULER.start()

# 사용자 정의 알람을 위한 백그라운드 스케쥴 시작
constant.USER_ALARM_SCHEDULER.start()

load_channel_alarms_from_file()
load_user_alarms_from_file()

# 로봇 서비스 시작
bot.run()
