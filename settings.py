"""Used to set secret variables, like the token"""
import sys
import getopt
import yaml

help_message = "settings.py -t <token>\n\n"\
            "-t --token <token>             set the token variable\n\n"\
            "-l --remote [enable_remote]    set the data:remote variable\n"\
            "-d --database <database_url>   set the data:db_url variable\n\n"\
            "-w --webhook [enable_webhook]  set the webhook:enabled variable (defaults to true)\n"\
            "-u --url [web_url]             set the webhook:url variable\n\n"\
            "-g --group [group_id]          set the meme:group_id variable\n"\
            "-c --channel [channel_id]      set the meme:channel_id variable\n\n"\
            "-p --path [settings_path]      set the path of the setting file (defaults to config/settings.yaml)\n" \
            "-r --revert                    set token and db_url to \"\" and enable_webhook to true"

new_token = ""
is_remote = True
url_database = ""
webhook_enabled = True
web_url = ""
group_id = ""
channel_id = ""
settings_path = "config/settings.yaml"

try:
    # get a list of argv with the related option flag
    opts, args = getopt.getopt(
        sys.argv[1:], "rht:d:p:w:g:u:c:l:",
        ["help", "revert", "token=", "database=", "path=", "webhook=", "group=", "url=", "channel=", "remote="])
except getopt.GetoptError:
    print(help_message)
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):  # show the help prompt
        print(help_message)
        sys.exit()
    elif opt in ("-p", "--path"):  # set the settings_path value (defaults to config/settings.yaml)
        settings_path = arg

try:
    with open(settings_path, "r") as yaml_file:
        config_map = yaml.load(yaml_file, Loader=yaml.SafeLoader)
except FileNotFoundError as e:
    print(["[error] settings: " + str(e)])

for opt, arg in opts:
    if opt in ("-t", "--token"):  # set the new_token value (defaults to "")
        new_token = arg if arg != "none" else ""
    elif opt in ("-d", "--database"):  # set url_database value (defaults to "")
        url_database = arg if arg != "none" else ""
    elif opt in ("-u", "--url"):  # set the group_id value to false...
        web_url = arg if arg != "none" else ""
    elif opt in ("-g", "--group"):  # set the group_id value to false...
        group_id = arg if arg != "none" else ""
    elif opt in ("-c", "--channel"):  # set the group_id value to false...
        channel_id = arg if arg != "none" else ""
    elif opt in ("-l", "--remote"):  # set the is_remote value to false...
        if arg.lower() in ("false", "no", "disable", "falso", "f", "n", "0", "-1"):  # if the parameter is in this list
            is_remote = False
    elif opt in ("-w", "--webhook"):  # set the webhook_enabled value to false...
        if arg.lower() in ("false", "no", "disable", "falso", "f", "n", "0", "-1"):  # if the parameter is in this list
            webhook_enabled = False
    elif opt in ("-r", "--revert"):  # reset all values to their default
        new_token = ""
        is_remote = False
        url_database = ""
        webhook_enabled = True
        web_url = ""
        group_id = ""
        channel_id = ""
        break
else:
    if not new_token:
        print("A token must provided with -t token")
        sys.exit(2)
    if is_remote and not url_database:
        print("If remote is enabled, a database_url must be provided\nYou can disable it with -l false")
        sys.exit(2)
    if webhook_enabled and not web_url:
        print("If webhook is enabled, a web_url must be provided\nYou can disable it with -w false")
        sys.exit(2)
    if (not group_id or not channel_id):
        print("A group_id and channel_id must be provided")
        sys.exit(2)

try:
    group_id = int(group_id) if group_id else ""
except ValueError as e:
    print("[error] settings: trying to set group_id\n" + str(e))
    sys.exit(2)

with open(settings_path, 'w') as yaml_file:
    config_map['token'] = new_token
    config_map['data']['remote'] = is_remote
    config_map['data']['db_url'] = url_database
    config_map['webhook']['enabled'] = webhook_enabled
    config_map['webhook']['url'] = web_url
    config_map['meme']['group_id'] = group_id
    config_map['meme']['channel_id'] = channel_id
    yaml.dump(config_map, yaml_file)
