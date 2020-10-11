"""Used to set secret variables, like the token"""
import sys
import getopt
import yaml

FALSE = ("false", "no", "disable", "falso", "f", "n", "0", "-1")

HELP = "settings.py -t <token>\n\n"\
            "-t --token <token>             set the token variable\n\n"\
            "-l --remote [enable_remote]    set the data:remote variable\n"\
            "-d --database <database_url>   set the data:db_url variable\n\n"\
            "-w --webhook [enable_webhook]  set the webhook:enabled variable (defaults to true)\n"\
            "-u --url [web_url]             set the webhook:url variable\n\n"\
            "-g --group [group_id]          set the meme:group_id variable\n"\
            "-c --channel [channel_id]      set the meme:channel_id variable\n\n"\
            "--test-api_id                  set the test:api_id variable (needed for testing)\n"\
            "--test-api_hash                set the test:api_hash variable (needed for testing)\n"\
            "--test-session                 set the test:session variable (needed for testing)\n"\
            "--test-tag                     set the test:tag variable (needed for testing)\n"\
            "--test-token                   set the test:token variable (needed for testing)\n\n"\
            "-p --path [settings_path]      set the path of the setting file (defaults to config/settings.yaml)\n" \
            "-r --revert                    set token and db_url to \"\" and enable_webhook to true"

new_token = ""
is_remote = True
url_database = ""
webhook_enabled = True
web_url = ""
group_id = 0
channel_id = ""
test_api_id = 0
test_api_hash = ""
test_session = ""
test_tag = ""
test_token = ""
settings_path = "config/settings.yaml"

try:
    # get a list of argv with the related option flag
    opts, args = getopt.getopt(sys.argv[1:], "rht:d:p:w:g:u:c:l:", [
        "help",
        "revert",
        "token=",
        "database=",
        "path=",
        "webhook=",
        "group=",
        "url=",
        "channel=",
        "remote=",
        "test-api_id=",
        "test-api_hash=",
        "test-session=",
        "test-tag=",
        "test-token=",
    ])
except getopt.GetoptError:
    print(HELP)
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):  # show the help prompt
        print(HELP)
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
        if arg.lower() in FALSE:  # if the parameter is in this list
            is_remote = False
    elif opt in ("-w", "--webhook"):  # set the webhook_enabled value to false...
        if arg.lower() in FALSE:  # if the parameter is in this list
            webhook_enabled = False
    elif opt == "--test-api_id":
        test_api_id = arg
    elif opt == "--test-api_hash":
        test_api_hash = arg
    elif opt == "--test-api_id":
        test_api_id = arg
    elif opt == "--test-session":
        test_session = arg
    elif opt == "--test-tag":
        test_tag = arg
    elif opt == "--test-token":
        test_token = arg
    elif opt in ("-r", "--revert"):  # reset all values to their default
        new_token = ""
        is_remote = False
        url_database = ""
        webhook_enabled = True
        web_url = ""
        group_id = 0
        channel_id = ""
        test_api_id = 0
        test_api_hash = ""
        test_session = ""
        test_tag = ""
        test_token = ""
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
    group_id = int(group_id)
except ValueError:
    print("[error] group_id must be an integer\n")
    sys.exit(2)
try:
    test_api_id = int(test_api_id)
except ValueError:
    print("[error] test_api_id must be an integer")
    sys.exit(2)

config_map['token'] = new_token
config_map['data']['remote'] = is_remote
config_map['data']['db_url'] = url_database
config_map['webhook']['enabled'] = webhook_enabled
config_map['webhook']['url'] = web_url
config_map['meme']['group_id'] = group_id
config_map['meme']['channel_id'] = channel_id
config_map['test']['api_id'] = test_api_id
config_map['test']['api_hash'] = test_api_hash
config_map['test']['session'] = test_session
config_map['test']['tag'] = test_tag
config_map['test']['token'] = test_token

with open(settings_path, 'w') as yaml_file:
    yaml.dump(config_map, yaml_file)
