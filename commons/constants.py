# 매터모스트 정보
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN: str = "dzme7z5wa38gmc8dswoupb55da"
BOT_TEAM: str = "1404"
MATTERMOST_URL = "https://recordame.cloud.mattermost.com"

# 채널 정보
RECORDAME_ID: str = "gttq5ttmdtyaiyrs4bz46n6gmh"
LOVELYLCM_ID: str = "npry7rpunpg3xes81os14gqbje"
CH_KORDLE_ID: str = "9aic13fzstdgmxro1c9f9i7yho"
CH_TOWN_SQUARE_ID: str = "7oc3baakktfxudigcjjdhmh4my"
CH_NOTIFICATIONS_ID: str = "9doiodruepdwmnbx8ejg395u7o"

# 알람 목록 저장용 변수
CHANNEL_ALARMS: dict = {}
# 알람 백그라운드 JOB
CHANNEL_ALARM_SCHEDULE = BackgroundScheduler()

# 사용자 정의 알람 목록 저장용 변수
USER_ALARMS: dict = {}
# 사용자 정의 알람 백그라운드 JOB
USER_ALARM_SCHEDULE = BackgroundScheduler()
