FROM joyzoursky/python-chromedriver

# 컨테이너의 시간대를 서울로 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install pip requirements
RUN mkdir /app
RUN mkdir /alarms

# ADD alarm /app/alarm
# ADD common /app/common
# ADD command /app/command
# ADD bot.py /app

ADD requirements.txt .
RUN pip install -r requirements.txt

# 메터모스트 웹소켓 SSL 연결 실패 패치
COPY lib-patch/usr/local/lib/python/site-packages/mattermostdriver/websocket.py /usr/local/lib/python3.10/site-packages/mattermostdriver

# 또는 docker -v HOST_파일경로:IMAGE_경로 명령어로 파일 연결
# docker run mattermost-bot --name hongzipsa --restart=alwayd -d  -v /Users/Gwangui/PycharmProjects/mattermost-bot-1404/app:/app -v /Users/Gwangui/PycharmProjects/mattermost-bot-1404/bot.log:/bot.log -v /Users/Gwangui/PycharmProjects/mattermost-bot-1404/alarms:/alarms

ENTRYPOINT ["python","/app/bot.py"]