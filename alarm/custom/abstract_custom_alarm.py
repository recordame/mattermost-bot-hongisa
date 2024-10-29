import datetime
import logging
import re
from abc import ABCMeta, abstractmethod

from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler
from mmpy_bot import Plugin, Message

from alarm.alarm_context import AlarmContext
from alarm.alarm_util import save_alarms_to_file_in_json
from common import constant
from common.utils import get_today_str


class AbstractCustomAlarm(Plugin, metaclass=ABCMeta):
    pattern_channel_id = '([a-zA-Z\\d]+)'
    pattern_alarm_id = '([가-힣a-zA-Z\\-_\\d]+)'
    pattern_digit_4 = '(\\d{4})'
    pattern_digit_1_2 = '(\\d{1,2})'
    pattern_day_xth = '(last|1st|2nd|3rd|\\dth)\\s(sun|mon|tue|wed|thu|fri|sat)'
    pattern_day = '(last|(\\d{1,2}([-,]\\d{1,2})*))'
    pattern_dow = '(\\*|((sun|mon|tue|wed|thu|fri|sat)([-,](sun|mon|tue|wed|thu|fri|sat))*))'
    pattern_date = '(\\d{8})'
    pattern_time = '(\\d+|\\*|(\\*|\\d+)/\\d+|\\d+([-,]\\d+)+)'
    pattern_interval_unit = '(\\d+(초|분|시간|일|주))'
    pattern_datetime = '(\\d{4}-\\d{1,2}-\\d{1,2}(T\\d{1,2}:\\d{1,2}:\\d{1,2})?)'
    pattern_msg = '(.*)'

    @abstractmethod
    def add_alarm(self):
        pass

    @abstractmethod
    def cancel_alarm(self):
        pass

    def schedule_alarm(
            self,
            message: Message,
            alarm_type: str,
            ctx: AlarmContext,
            alarm_contexts: dict,
            alarm_scheduler: BackgroundScheduler,
            recovery_mode: bool = False
    ):
        # 모든 유형 대상 신규 항목 추가 기능

        job = alarm_scheduler.get_job(ctx.job_id)
        # 동일한 항목이 존재 하는 경우, 안내 메시지 출력 후 종료
        if job is not None:
            try:
                existing_ctx: AlarmContext = constant.CHANNEL_ALARMS[ctx.post_to][ctx.id]
            except KeyError:
                try:
                    existing_ctx: AlarmContext = constant.USER_ALARMS[ctx.post_to][ctx.id]
                except KeyError:
                    existing_ctx: AlarmContext = constant.EPHEMERAL_ALARMS[ctx.post_to][ctx.id]

            self.driver.direct_message(
                message.user_id, f'이미 등록된 항목이 있어요! 취소 후 재등록해주세요.\n'
                                 f'**항목 정보**\n'
                                 f'{existing_ctx.get_info()}\n'
                                 f'   - [취소하기](https://{constant.FLASK_SERVER_IP}/hongisa/alarm/{existing_ctx.creator_id}/{existing_ctx.post_to}/{existing_ctx.id}/cancel)'
            )

            return

        # 신규 항목인 경우 등록 절차 계속
        message_function = self.get_message_function(ctx.message, ctx.post_to, message)

        try:
            alarm_job = create_alarm_job(ctx, alarm_scheduler, message_function)

            if ctx.job_status == '정지':
                alarm_job.pause()
        except:
            self.driver.direct_message(ctx.creator_id, '인자 형식이 잘못되어 등록할 수 없었어요 :crying_cat_face:\n `도움말` `help` `?` 중 하나를 입력해 보세요.')
            return

        # 동일한 목적지에 등록된 항목 리스트 획득
        alarms = alarm_contexts.get(ctx.post_to)

        # 신규 항목 추가
        if alarms is not None:
            alarm_contexts[ctx.post_to].update({ctx.id: ctx})
        else:
            alarm_contexts.update({ctx.post_to: {ctx.id: ctx}})

        logging.info(f'[stat] {alarm_type}알람등록({ctx.id})')

        if not recovery_mode:
            # 파일로 백업
            save_alarms_to_file_in_json(alarm_type, alarm_contexts)

            # 예약 메시지인 경우
            if alarm_type == '예약':
                self.driver.direct_message(
                    ctx.creator_id,
                    f'`{ctx.id}` 을/를 `{ctx.day[0:4]}-{ctx.day[4:6]}-{ctx.day[6:8]} {ctx.hour}:{ctx.minute}:{ctx.second}`에 전달해드릴게요 :dizzy:\n'
                    f'(단, 과거 시간을 설정하는 경우, 예약이 취소돼요!)'
                )

                return

            # 주기 알람인 경우
            if ctx.interval != '':
                self.driver.direct_message(
                    ctx.creator_id,
                    f'`{ctx.id}` 을/를 `{ctx.interval_from}` 부터 매 `{ctx.interval}` 마다 전달해드릴게요 :dizzy:'
                )

                return

            # 기본 알람인 경우
            self.driver.direct_message(
                ctx.creator_id,
                f'`{ctx.id}` 을/를 `{ctx.day} {ctx.hour}:{ctx.minute}:{ctx.second}` 에 전달해드릴게요 :dizzy:'
            )

    def suspend_alarm(
            self,
            message: Message,
            alarm_type: str,
            post_to: str,
            alarm_id,
            alarm_contexts: dict,
            alarm_scheduler: BackgroundScheduler
    ):
        # 개인 알람 전용 알람 일시정지 기능

        # 알람을 특정하지 않은 경우 모든 알람 일시정지
        if alarm_id == '' or alarm_id is None:
            try:
                alarms: dict = alarm_contexts[post_to]
                dirty: bool = False

                for alarm in list(alarms.values()):
                    if alarm.job_status == '실행':
                        dirty = True

                        alarm_scheduler.get_job(alarm.job_id).pause()
                        alarm.job_status = '정지'

                        self.driver.direct_message(message.user_id, f'`{alarm_id}` 항목이 정지되었어요 :red_circle:')

                if dirty:
                    save_alarms_to_file_in_json(alarm_type, alarm_contexts)
                else:
                    self.driver.direct_message(message.user_id, f'모든 항목이 정지상태예요 :wink:')

            except KeyError:
                self.driver.direct_message(message.user_id, f'등록된 항목이 없어요 :crying_cat_face:')
        # 알람이 특정된 경우 해당 알람만 일시정지
        else:
            job_id = post_to + "_" + alarm_id
            job = alarm_scheduler.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, f'등록된 항목이 없어요 :crying_cat_face:')
            else:
                job.pause()

                ctx = alarm_contexts[post_to][alarm_id]
                ctx.job_status = '정지'

                save_alarms_to_file_in_json(alarm_type, alarm_contexts)

                self.driver.direct_message(message.user_id, f'`{alarm_id}` 항목이 정지되었어요 :red_circle:')

    def continue_alarm(
            self,
            message: Message,
            alarm_type: str,
            post_to: str,
            alarm_id,
            alarm_contexts: dict,
            alarm_scheduler: BackgroundScheduler
    ):
        # 개인 알람 전용 알람 재개 기능

        if alarm_id == '' or alarm_id is None:
            try:
                alarms: dict = alarm_contexts[post_to]
                dirty: bool = False

                for alarm in list(alarms.values()):
                    if alarm.job_status == '정지':
                        dirty = True

                        alarm_scheduler.get_job(alarm.job_id).resume()
                        alarm.job_status = '실행'

                        self.driver.direct_message(message.user_id, f'`{alarm_id}` 항목이 재개되었어요 :recycle:')

                if dirty:
                    save_alarms_to_file_in_json(alarm_type, alarm_contexts)
                else:
                    self.driver.direct_message(message.user_id, f'모든 항목이 실행중이네요 :wink:')

            except KeyError:
                self.driver.direct_message(message.user_id, f'등록된 항목이 없어요 :crying_cat_face:')

        else:
            job_id = post_to + '_' + alarm_id
            job = alarm_scheduler.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, f'등록된 항목이 없어요 :crying_cat_face:')
            else:
                job.resume()

                ctx = alarm_contexts[post_to][alarm_id]
                ctx.job_status = '실행'

                save_alarms_to_file_in_json(alarm_type, alarm_contexts)

                self.driver.direct_message(message.user_id, f'`{alarm_id}` 항목이 재개되었어요 :recycle:')

    def unschedule_alarm(
            self, message: Message,
            alarm_type: str,
            post_to: str,
            alarm_id: str,
            alarm_contexts: dict,
            alarm_scheduler: BackgroundScheduler
    ):
        # 모든 유형(채널/개인/채널예약/개인예약) 대상 항목 제거 기능

        # 개인알람에 대하여, 항목을 특정하지 않은 경우 일괄 삭제
        if alarm_id == '' or alarm_id is None:
            try:
                alarms: dict = alarm_contexts[post_to]

                for alarm in list(alarms.values()):
                    alarm_scheduler.remove_job(alarm.job_id)
                    del alarm_contexts[post_to][alarm.id]

                    save_alarms_to_file_in_json(alarm_type, alarm_contexts)

                    self.driver.direct_message(message.user_id, f'`{alarm.id}` 항목이 삭제되었어요 :skull_and_crossbones:')

                    logging.info(f'[stat] {alarm_type}알람삭제({alarm.id})')

            except KeyError:
                self.driver.direct_message(message.user_id, f'등록된 항목이 없어요 :crying_cat_face:')
        # 항목이 특정된 경우
        else:
            job_id = post_to + "_" + alarm_id
            job = alarm_scheduler.get_job(job_id)

            if job is None:
                self.driver.direct_message(message.user_id, f'등록된 항목이 없어요 :crying_cat_face:')
                return

            alarm: AlarmContext = alarm_contexts[post_to][alarm_id]

            alarm_scheduler.remove_job(job_id)
            del alarm_contexts[post_to][alarm_id]

            save_alarms_to_file_in_json(alarm_type, alarm_contexts)

            self.driver.direct_message(message.user_id, f'`{alarm_id}` 항목이 삭제되었어요 :skull_and_crossbones:')

            if alarm_type != '개인':
                if alarm.creator_name != message.sender_name:
                    # 알람 삭제 요청자가 알람 등록자와 다른경우, 등록자에게 알림
                    self.driver.direct_message(
                        alarm.creator_id,
                        f'등록하신 `{alarm_id}` 항목이 {message.sender_name}님에 의해 삭제되었어요 :skull_and_crossbones:\n\n'
                        f'**삭제 항목**\n'
                        f'{alarm.get_info()}\n'
                    )

            logging.info(f'[stat] {alarm_type}알람삭제({alarm_id})')

    def get_message_function(self, alarm_message: str, post_to: str, message: Message = None):
        # 치환할 메시지가 존재하는 경우
        if '$날짜' in alarm_message:
            before_insertion = alarm_message.split('$날짜')[0].replace('\\n', '\n')
            after_insertion = alarm_message.split('$날짜')[1].replace('\\n', '\n')

            return lambda: self.post_message(post_to, alarm_message=f'{before_insertion}{get_today_str()}{after_insertion}')
        elif '$미사' in alarm_message:
            before_insertion = alarm_message.split('$미사')[0].replace('\\n', '\n')
            after_insertion = alarm_message.split('$미사')[1].replace('\\n', '\n')

            return lambda: self.post_message(post_to, alarm_message=f'{before_insertion}{str(constant.BUILTIN_ALARM_INSTANCES.get("미사").generate_message()).removeprefix("@here").strip(" ")}{after_insertion}')
        else:
            return lambda: self.post_message(post_to, alarm_message)

    def post_message(self, post_to: str, alarm_message: str):
        alarm_message = alarm_message.replace('\\n', '\n')

        try:
            self.driver.channels.get_channel(post_to)
            self.driver.create_post(post_to, alarm_message)
            logging.info(f'채널알람 전송 완료 - 목적지: {post_to}, 메시지: {alarm_message}')
        except:
            self.driver.direct_message(post_to, alarm_message)
            logging.info(f'개인알람 전송 완료 - 목적지: {post_to}, 메시지: {alarm_message}')


######################################################

def create_alarm_job(ctx: AlarmContext, alarm_scheduler: BackgroundScheduler, message_function) -> Job:
    schedule_type: str

    if ctx.interval != '':
        schedule_type = 'interval'
    elif re.match('^(\\d{8})$', ctx.day):
        schedule_type = 'date'
    else:
        schedule_type = 'cron'

    if schedule_type == 'interval':
        if re.match('^\\d{4}-\\d{2}-\\d{2}(T\\d{2}:\\d{2}:\\d{2})?$', ctx.interval_from):
            if re.match('^\\d+초$', ctx.interval):
                seconds_to_wait = int(ctx.interval.replace('초', ''))
            elif re.match('^\\d+분$', ctx.interval):
                seconds_to_wait = int(ctx.interval.replace('분', '')) * 60
            elif re.match('^\\d+시간$', ctx.interval):
                seconds_to_wait = int(ctx.interval.replace('시간', '')) * 60 * 60
            elif re.match('^\\d+일$', ctx.interval):
                seconds_to_wait = int(ctx.interval.replace('일', '')) * 60 * 60 * 24
            elif re.match('^\\d+주$', ctx.interval):
                seconds_to_wait = int(ctx.interval.replace('주', '')) * 60 * 60 * 24 * 7
            else:
                raise ValueError

            return alarm_scheduler.add_job(
                id=ctx.job_id,
                func=message_function,
                trigger="interval",
                seconds=seconds_to_wait,
                start_date=ctx.interval_from,
                misfire_grace_time=60
            )
        else:
            raise ValueError
    elif schedule_type == 'date':
        if re.match('^(\\d{8})$', ctx.day):
            return alarm_scheduler.add_job(
                id=ctx.job_id,
                func=message_function,
                trigger='date',
                run_date=datetime.datetime(int(ctx.day[0:4]), int(ctx.day[4:6]), int(ctx.day[6:8]), int(ctx.hour),
                                           int(ctx.minute), int(ctx.second)),
                misfire_grace_time=60
            )
        else:
            raise ValueError
    else:
        if re.match('^((1st|2nd|3rd|\\dth|last)\\s(sun|mon|tue|wed|thu|fri|sat))|last$', ctx.day) \
                or re.match('^(\\d{1,2})(-\\d{1,2})?$', ctx.day) \
                or re.match('^(\\d{1,2})(,\\d{1,2})?$', ctx.day):
            return alarm_scheduler.add_job(
                id=ctx.job_id,
                func=message_function,
                trigger='cron',
                day=ctx.day,
                hour=ctx.hour,
                minute=ctx.minute,
                second=ctx.second,
                misfire_grace_time=60
            )
        elif re.match('^(sun|mon|tue|wed|thu|fri|sat|,|-)+|\\*$', ctx.day):
            return alarm_scheduler.add_job(
                id=ctx.job_id,
                func=message_function,
                trigger='cron',
                day_of_week=ctx.day,
                hour=ctx.hour,
                minute=ctx.minute,
                second=ctx.second,
                misfire_grace_time=60
            )
        else:
            raise ValueError
