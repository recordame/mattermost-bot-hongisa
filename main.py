# !/usr/bin/env python

from mmpy_bot import Bot, Settings

import constant
from alarms import Alarms
from help import Help
from kordle import KordleAlarm
from mass import MassAlarm
from medicine import MedicineAlarm
from weather import WeatherAlarm

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
    plugins=[KordleAlarm(), MedicineAlarm(), WeatherAlarm(), MassAlarm(), Help(), Alarms()],
)
bot.run()
