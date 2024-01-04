from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN: str = 'fj6kf9txdiygu8ga8ca7oth1qr'
BOT_TEAM: str = 'hongeejanggun'
MATTERMOST_URL = 'http://recordame.synology.me'
ADMINS: list = ['recordame']

# 채널 정보
CH_KORDLE_ID: str = 'b9j1mpuxdjbxdkjr4tdzht9uey'
CH_NOTIFICATIONS_ID: str = 'np83b9aggif98j1omio1m3zozo'
CH_JINHA_ID: str = 'wske4xkn3tn7br5t1h3f4czx4o'

BUILTIN_ALARM_INSTANCE: dict[str, object] = {}

# 채널 알람 목록 저장용 변수
CHANNEL_ALARMS: dict[str, dict[str, object]] = {}
# 채널 알람 백그라운드 JOB
CHANNEL_ALARM_SCHEDULER = BackgroundScheduler(timezone='Asia/Seoul')

# 개인 알람 목록 저장용 변수
USER_ALARMS: dict[str, dict[str, object]] = {}
# 개인 알람 백그라운드 JOB
USER_ALARM_SCHEDULER = BackgroundScheduler(timezone='Asia/Seoul')
