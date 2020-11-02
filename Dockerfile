FROM python:3.8.5-slim-buster

ARG TOKEN=none
ARG DATABASE_URL=none
ARG WEB_URL=none
ARG GROUP_ID=none
ARG CHANNEL_ID=none
ARG CHANNEL_GROUP_ID=none

ENV BOT_DIR    /app

WORKDIR $BOT_DIR

COPY requirements.txt .
#Install requirements
RUN pip3 install -r requirements.txt

COPY . .
#Setup settings and databases
RUN mv data/db/sqlite.db.dist data/db/sqlite.db &&\
  mv config/settings.yaml.dist config/settings.yaml &&\
  python3 settings.py ${TOKEN} ${GROUP_ID} ${CHANNEL_ID} ${CHANNEL_GROUP_ID} -r -d ${DATABASE_URL} -w -u ${WEB_URL}

#Cleanup
RUN rm settings.py &&\
  rm -r tests

#Start the bot
CMD [ "python3", "main.py" ]