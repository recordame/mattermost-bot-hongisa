# !/usr/bin/env python

from mmpy_bot import Bot, Settings

from commands.alarms import Alarms
from commands.currency import CurrencyAlarm
from commands.help import Help
from commands.kordle import KordleAlarm
from commands.mass import MassAlarm
from commands.medicine import MedicineAlarm
from commands.plan import Plan
from commands.weather import WeatherAlarm
from commons import constant

bot = Bot(
    settings=Settings(
        MATTERMOST_URL=constant.MATTERMOST_URL,
        MATTERMOST_PORT=443,
        MATTERMOST_API_PATH="/api/v4",
        BOT_TOKEN=constant.BOT_TOKEN,
        BOT_TEAM=constant.BOT_TEAM,
        SSL_VERIFY=False,
        LOG_FILE="./log.txt"
    ),
    plugins=[KordleAlarm(), MedicineAlarm(), WeatherAlarm(), MassAlarm(), Help(), Alarms(), CurrencyAlarm(), Plan()],
)
bot.run()
