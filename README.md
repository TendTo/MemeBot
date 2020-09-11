# Meme bot

**Meme bot** [**@tendTo_bot**](https://telegram.me/tendTo_bot) is a Telegram meme bot

### Using the live version
The bot is live on Telegram with the username [**@tendTo_bot**](https://telegram.me/tendTo_bot).
To see the posts, once published, check [**Meme channel di meme_bo**](https://t.me/memchannel_bot)
Send **'/start'** to start it, **'/help'** to see a list of commands.
Please note that the commands and their answers are in Italian.

---

### :wrench: Setting up a local istance

##### System requirements
- Python 3
- python-pip3
- [optional] sphinx (for documentation purposes)

##### Install with *pip3*
Listed in requirements.txt
- python-telegram-bot
- requests
- PyYAML
- psycopg2-binary

#### Steps:
- Clone this repository
- Rename "data/db/sqlite.db.dist" in "data/db/sqlite.db"
- Rename "config/settings.yaml.dist" in "config/settings.yaml" and edit the desired parameters
	- **data:**
		- **db_url:** url of your postgres database (false recommended for local)
		- **remote** whether the data will be saved remotely (postgres) or locally (mysql)
	- **debug:**
		- **db_log:** save each and every message in a log file. Make sure the path "logs/messages.log" is valid before putting it to 1
		- **local_log:** /
	- **meme:**
		- **channel_id:** tag of your channel, @ included
		- **enabled:** whether the memebot is enabled
		- **group_id:** id of the admin group the memebot will use
		- **n_votes:** votes needed to approve/reject a pending post
		- **reset_on_load:** whether or not the database should reset every time the bot launches
	- **token:** the token for your telegram bot
	- **webhook:**
		- **enabled:** whether or not the bot should use webhook (false recommended for local)
		- **url:** the url used by the webhook
- **Run**`python3 main.py`

#### [Optional] Generate documentation:
- **Run**`sphinx-apidoc -o docs .` to update the documentation based on the index.rts. If you didn't modify anything, you can skip this
- **Run**`sphinx-build -b html docs docs/_build` to update the make file
- **Run**`docs/make html` to produce the documentation

### :whale: Setting up a Docker container

##### System requirements
- Docker


#### Steps:
- Clone this repository
- In "config/settings.yaml.dist", edit the desired values. Be mindful that the one listed below will overwrite the ones in "config/settings.yaml.dist", even if they aren't used in the command line
- **Run** `docker build --tag botimage --build-arg TOKEN=<token_arg> [...] .` 

| In the command line <br>(after each --build-arg) | Type | Function | Optional |
| --- | --- | --- | --- |
| **TOKEN=<token_args>** | string | the token for your telegram bot | REQUIRED |
| **WEBHOOK_ENABLED=<webhook_enabled>** | bool | whether or not the bot should use webhook<br>(false recommended for local) | OPTIONAL - defaults to false |
| **WEB_URL=<web_url>** | string | the url used by the webhook | REQUIRED IF webhook_enabled = true |
| **DATA_REMOTE=<data_remote>** | bool | whether the data will be saved remotely (postgres) or locally (mysql)<br>(false recommended for local) | OPTIONAL - defaults to false |
| **DATABASE_URL=<db_url>** | string | url of your postgres database | REQUIRED IF data_remote = true |
| **MEME_ENABLED=<meme_enabled>** | bool | whether the memebot is enabled | OPTIONAL - defaults to true |
| **GROUP_ID=<group_id>** | int | id of the admin group the memebot will use | REQUIRED IF meme_enabled = true |
| **CHANNEL_ID=<channel_id>** | string | tag of your channel, @ included | REQUIRED IF meme_enabled = true |
- **Run**`docker run -d --name botcontainer botimage`

#### To stop/remove the container:
- **Run** `docker stop botcontainer` to stop the container
- **Run** `docker rm -f botcontainer` to remove the container

## :thought_balloon: Inspired by
[Telegram-SpottedDMI-Bot](https://github.com/UNICT-DMI/Telegram-SpottedDMI-Bot)

## :bust_in_silhouette: Author

[Tend](https://github.com/TendTo)

## :balance_scale: License

[MIT](https://choosealicense.com/licenses/mit/)
