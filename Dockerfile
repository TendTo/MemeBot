FROM python:3.8.5

ARG TOKEN
ARG DATA_REMOTE=1
ARG DATABASE_URL
ARG WEBHOOK_ENABLED=1
ARG WEB_URL
ARG MEME_ENABLED=1
ARG GROUP_ID
ARG CHANNEL_ID

ENV BOT_DIR    /app

WORKDIR $BOT_DIR

COPY . .
#Install requirements
RUN pip3 install -r ${BOT_DIR}/requirements.txt

#Setup settings and databases
RUN mv data/db/sqlite.db.dist data/db/sqlite.db &&\
  mv config/settings.yaml.dist config/settings.yaml &&\
  python3 settings.py -t ${TOKEN} -l ${DATA_REMOTE} -d ${DATABASE_URL} -w ${WEBHOOK_ENABLED} -u ${WEB_URL} -m ${MEME_ENABLED} -g ${GROUP_ID} -c ${CHANNEL_ID}

#Cleanup
RUN rm settings.py &&\
  rm -r tests docs

#Start the bot
CMD [ "python3", "main.py" ]