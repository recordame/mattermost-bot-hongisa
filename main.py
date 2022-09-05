# !/usr/bin/env python

from mmpy_bot import Bot, Settings

import constant
from help import Help
from kordle import Kordle
from mass import Mass
from weather import Weather

bot = Bot(
    settings=Settings(
        MATTERMOST_URL=constant.MATTERMOST_URL,
        MATTERMOST_PORT=443,
        MATTERMOST_API_PATH="/api/v4",
        BOT_TOKEN=constant.BOT_TOKEN,
        BOT_TEAM=constant.BOT_TEAM,
        SSL_VERIFY=True,
    ),
    plugins=[Kordle(), Weather(), Mass(), Help()],
)
bot.run()
