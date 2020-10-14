# Meme bot

**Meme bot** [**@tendTo_bot**](https://telegram.me/tendTo_bot) is a Telegram meme bot

### Using the live version
The bot is live on Telegram with the username [**@tendTo_bot**](https://telegram.me/tendTo_bot).
To see the posts, once published, check [**Meme channel di meme_bot**](https://t.me/memchannel_bot)
Send **'/start'** to start it, **'/help'** to see a list of commands.
Please note that the commands and their answers are in Italian.

## Table of contents

- **[:wrench: Setting up a local istance](#wrench-setting-up-a-local-istance)**
- **[:whale: Setting up a Docker container](#whale-setting-up-a-docker-container)**
- **[:bar_chart: _\[Optional\]_ Setting up testing](#bar_chart-optional-setting-up-testing)**
- **[:twisted_rightwards_arrows: About Pull Requests](#twisted_rightwards_arrows-about-pull-requests)**

---

## :wrench: Setting up a local istance

#### System requirements
- [Python 3 (3.8.5)](https://www.python.org/downloads/)
- python-pip3

#### Install with *pip3*
Listed in requirements.txt
- [python-telegram-bot](https://pypi.org/project/python-telegram-bot/)
- [requests](https://pypi.org/project/requests/)
- [PyYAML](https://pypi.org/project/PyYAML/)
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/)

### Steps:
- Clone this repository
- Rename "data/db/sqlite.db.dist" in "data/db/sqlite.db"
- Rename "config/settings.yaml.dist" in "config/settings.yaml" and edit the desired parameters:
```yaml
data:
  db_url: url of your postgres database (false recommended for local)
  remote: whether the data will be saved remotely (postgres) or locally (mysql)

debug:
  db_log: save each and every message in a log file. Make sure the path "logs/messages.log" is valid before putting it to 1
  local_log: /

meme:
  channel_id: tag of your channel, @ included
  enabled: whether the memebot is enabled
  group_id: id of the admin group the memebot will use
  n_votes: votes needed to approve/reject a pending post
  reset_on_load: whether or not the database should reset every time the bot launches

test:
  api_hash: hash of the telegram app used for testing
  api_id: id of the telegram app used for testing
  remote:  whether you want to test the remote database, the local one or both
  session: session of the telegram app used for testing
  tag: tag of the telegram bot used for testing. Include the '@' character
  token: token for the telegram bot used for testing

token: the token for your telegram bot

webhook:
  enabled: whether or not the bot should use webhook (false recommended for local)
  url: the url used by the webhook
```
- **Run** `python3 main.py`

## :whale: Setting up a Docker container

#### System requirements
- Docker


### Steps:
- Clone this repository
- In "config/settings.yaml.dist", edit the desired values. Be mindful that the one listed below will overwrite the ones in "config/settings.yaml.dist", even if they aren't used in the command line
- **Run** `docker build --tag botimage --build-arg TOKEN=<token_arg> [...] .` 

| In the command line <br>(after each --build-arg) | Type | Function | Optional |
| --- | --- | --- | --- |
| **TOKEN=<token_args>** | string | the token for your telegram bot | REQUIRED |
| **WEBHOOK_ENABLED=<webhook_enabled>** | bool | whether or not the bot should use webhook<br>(false recommended for local) | OPTIONAL - defaults to false |
| **WEB_URL=<web_url>** | string | the url used by the webhook | REQUIRED IF<br>webhook_enabled = true |
| **DATA_REMOTE=<data_remote>** | bool | whether the data will be saved remotely (postgres) or locally (mysql)<br>(false recommended for local) | OPTIONAL - defaults to false |
| **DATABASE_URL=<db_url>** | string | url of your postgres database | REQUIRED IF<br>data_remote = true |
| **GROUP_ID=<group_id>** | int | id of the admin group the memebot will use | REQUIRED |
| **CHANNEL_ID=<channel_id>** | string | tag of your channel, @ included | REQUIRED |
- **Run** `docker run -d --name botcontainer botimage`

### To stop/remove the container:
- **Run** `docker stop botcontainer` to stop the container
- **Run** `docker rm -f botcontainer` to remove the container

## :bar_chart: _[Optional]_ Setting up testing

### Create a Telegram app:

#### Steps:
- Sign in your Telegram account with your phone number **[here](https://my.telegram.org/auth)**. Then choose “API development tools”
- If it is your first time doing so, it will ask you for an app name and a short name, you can change both of them later if you need to. Submit the form when you have completed it
- You will then see the **api_id** and **api_hash** for your app. These are unique to your app, and not revocable.
- Put those values in the _conf/settings.yaml_ file for local or in the _conf/settings.yaml.dist_ file if you are setting up a docker container
```yaml
test:
    api_hash: HERE
    api_id: HERE
...
```
- Copy the file _tests/conftest.py_ in the root folder and **Run** `python3 conftest.py `. Follow the procedure and copy the session string it provides in the settings file:
```yaml
test:
...
    session: HERE
...
```
- You can then delete the _conftest.py_ file present in the root folder, you won't need it again
- Edit the remaining values in the file as you see fit

**Check [here](https://dev.to/blueset/how-to-write-integration-tests-for-a-telegram-bot-4c0e) you you want to have more information on the steps above**

### In local:

#### Install with *pip3*
- [telethon](https://pypi.org/project/Telethon/)
- [pytest](https://pypi.org/project/pytest/)
- [pytest-asyncio](https://pypi.org/project/pytest-asyncio/)

#### Steps:
- **Run** `pytest`

### In a docker container:

#### Steps:
- Add telethon, pytest and pytest-asyncio to the requirements.txt file
- Access the container and **Run** `pytest` or edit the Dockerfile to do so

## :twisted_rightwards_arrows: About Pull Requests
Upon submitting a Pull Request, a github action will be triggered. The workflow will run all the tests to make sure everything still works correctly

The workflow will fail if your repository lacks even one of the following secrets:
| SECRET | Type | Function |
| --- | --- | --- |
| **API_ID** | int | id of the telegram app used for testing |
| **API_HASH** | string | hash of the telegram app used for testing |
| **SESSION** | string | session of the telegram app used for testing |
| **TEST_TAG** | string | tag of the bot used for testing |
| **TEST_TOKEN** | string | token for the bot used for testing |

**To pass the workflow is not mandatory, but is highly suggested**

## :thought_balloon: Inspired by
[Telegram-SpottedDMI-Bot](https://github.com/UNICT-DMI/Telegram-SpottedDMI-Bot)

## :bust_in_silhouette: Author

[Tend](https://github.com/TendTo)

## :balance_scale: License

[MIT](https://choosealicense.com/licenses/mit/)
