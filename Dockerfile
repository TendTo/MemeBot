FROM python:3.8.5

ARG TOKEN=none
ARG DATA_REMOTE=false
ARG DATABASE_URL=none
ARG WEBHOOK_ENABLED=false
ARG WEB_URL=none
ARG MEME_ENABLED=true
ARG GROUP_ID=none
ARG CHANNEL_ID=none

ENV BOT_DIR    /app

WORKDIR $BOT_DIR

COPY requirements.txt .
#Install requirements
RUN pip3 install -r requirements.txt

COPY . .
#Setup settings and databases
RUN mv data/db/sqlite.db.dist data/db/sqlite.db &&\
  mv config/settings.yaml.dist config/settings.yaml &&\
  python3 settings.py -t ${TOKEN} -l ${DATA_REMOTE} -d ${DATABASE_URL} -w ${WEBHOOK_ENABLED} -u ${WEB_URL} -m ${MEME_ENABLED} -g ${GROUP_ID} -c ${CHANNEL_ID}

#Cleanup
RUN rm settings.py &&\
  rm -r tests docs

#Start the bot
CMD [ "python3", "main.py" ]