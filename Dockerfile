# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-alpine

ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install pip requirements
RUN mkdir /app
ADD commands /app/commands
ADD commons /app/commons
ADD main.py /app

ADD requirements.txt .
RUN pip install -r requirements.txt

COPY lib-patch/usr/local/lib/python3.10/site-packages/mattermostdriver/websocket.py /usr/local/lib/python3.10/site-packages/mattermostdriver

ENTRYPOINT ["python","/app/main.py"]
