# !/usr/bin/env python

from mmpy_bot import Bot, Settings

from commands.alarms import Alarms
from commands.currency import CurrencyAlarm
from commands.help import Help
from commands.kordle import KordleAlarm
from commands.mass import MassAlarm
from commands.medicine import MedicineAlarm
from commands.my_alarm import MyAlarm
from commands.weather import WeatherAlarm
from commons import constant

# 로봇 설정
bot = Bot(
    settings=Settings(
        MATTERMOST_URL=constant.MATTERMOST_URL,
        MATTERMOST_PORT=443,
        MATTERMOST_API_PATH="/api/v4",
        BOT_TOKEN=constant.BOT_TOKEN,
        BOT_TEAM=constant.BOT_TEAM,
        SSL_VERIFY=False,
        LOG_FILE="./bot.log"
    ),
    plugins=[KordleAlarm(), MedicineAlarm(), WeatherAlarm(), MassAlarm(), Help(), Alarms(), CurrencyAlarm(), MyAlarm()],
)

# 알림을 위한 백그라운드 스케쥴 시작
constant.SCHEDULE.start()

# 사용자 정의 알림을 위한 백그라운드 스케쥴 시작
constant.MY_SCHEDULE.start()

# 로봇 서비스 시작
bot.run()
