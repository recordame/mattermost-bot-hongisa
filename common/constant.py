from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# 웹서버 정보
FLASK_SERVER_IP: str = 'recordame.ddns.net'
FLASK_SERVER_PORT: str = '8006'

KR_TIME_ZONE = timezone('Asia/Seoul')

BOT_TOKEN: str = 'fj6kf9txdiygu8ga8ca7oth1qr'
BOT_TEAM: str = 'hongeejanggun'
MATTERMOST_URL = 'http://172.22.0.2'
MATTERMOST_PORT = 8065
ADMINS: list = ['recordame']

# 채널 정보
CH_KORDLE_ID: str = 'b9j1mpuxdjbxdkjr4tdzht9uey'
CH_NOTIFICATIONS_ID: str = 'np83b9aggif98j1omio1m3zozo'
CH_JINHA_ID: str = 'wske4xkn3tn7br5t1h3f4czx4o'

# 빌트인 유형 알람 인스턴스 저장용 변수 : AbstractAlarm
BUILTIN_ALARM_INSTANCES: dict[str, object] = {}

# 홍집사 백그라운드 작업 JOB
BACKGROUND_SCHEDULER = BackgroundScheduler(timezone='Asia/Seoul')

# 채널 알람 목록 저장용 변수
CHANNEL_ALARMS: dict[str, dict[str, object]] = {}
# 채널 알람 백그라운드 JOB
CHANNEL_ALARM_SCHEDULER = BackgroundScheduler(timezone='Asia/Seoul')

# 개인 알람 목록 저장용 변수
USER_ALARMS: dict[str, dict[str, object]] = {}
# 개인 알람 백그라운드 JOB
USER_ALARM_SCHEDULER = BackgroundScheduler(timezone='Asia/Seoul')

# 메시지 예약 목록 저장용 변수 : AlarmContext
EPHEMERAL_ALARMS: dict[str, dict[str, object]] = {}
# 메시지 예약 백그라운드 JOB
EPHEMERAL_ALARM_SCHEDULER = BackgroundScheduler(timezone='Asia/Seoul')

# 할일목록 알람 백그라운드 JOB
TODO_ALARM_SCHEDULER = BackgroundScheduler(timezone='Asia/Seoul')
