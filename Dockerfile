FROM python-chrome

# 컨테이너의 시간대를 서울로 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install pip requirements
RUN mkdir /app
ADD alarm /app/alarm
ADD common /app/common
ADD command /app/command
ADD bot.py /app

RUN mkdir /alarms

ADD requirements.txt .
RUN pip install -r requirements.txt

# 메터모스트 웹소켓 SSL 연결 실패 패치
COPY lib-patch/usr/local/lib/python/site-packages/mattermostdriver/websocket.py /usr/local/lib/python3.10/site-packages/mattermostdriver

# 또는 docker -v HOST_파일경로:IMAGE_경로 명령어로 파일 연결
# docker run -v alarms:/alarms --name bot -d bot


ENTRYPOINT ["python","/app/bot.py"]
