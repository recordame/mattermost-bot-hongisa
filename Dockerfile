FROM python-chrome

# 컨테이너의 시간대를 서울로 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install pip requirements
RUN mkdir /app
ADD commands /app/commands
ADD commons /app/commons
ADD main.py /app

ADD requirements.txt .
RUN pip install -r requirements.txt

# 메터모스트 웹소켓 SSL 연결 실패 패치
COPY lib-patch/usr/local/lib/python3.10/site-packages/mattermostdriver/websocket.py /usr/local/lib/python3.10/site-packages/mattermostdriver

COPY channel_alarms.json /
COPY user_alarms.json /

ENTRYPOINT ["python","/app/main.py"]
