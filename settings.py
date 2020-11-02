"""Used to set secret variables, like the token, in the config/settings.yaml file"""
import sys
import argparse
import yaml


def create_argparser() -> argparse.ArgumentParser:
    """Generates the appropriate argparser

    Returns:
        argparse.ArgumentParser: the argparser used to parse the arguments
    """
    parser = argparse.ArgumentParser(description="Settings utility to edit the config/settings.yaml file", allow_abbrev=True)
    parser.add_argument('token', help="the token of your telegram bot")
    parser.add_argument('group_id', type=int, help="chat id of the group used by the admins")
    parser.add_argument('channel_id', type=int, help="chat id of the channel the bot will post to")
    parser.add_argument('channel_group_id', type=int, help="chat id of the group that will host the channel's comments")

    # Used to deploy to Heroku
    parser.add_argument('-r', '--remote', help="enable the remote database", action='store_true', default=False)
    parser.add_argument('-d', '--database', help="the access point to the remote database (required if -r)")
    parser.add_argument('-w', '--webhook', help="enable the webhook", action='store_true', default=False)
    parser.add_argument('-u', '--urlwebhook', help="the url used by the webhook (required if -w)")

    # Used for testing
    parser.add_argument('--test_api_hash', help="hash of the telegram app used for testing")
    parser.add_argument('--test_api_id', type=int, help="id of the telegram app used for testing")
    parser.add_argument('--test_session', help="session of the telegram app used for testing")
    parser.add_argument('--test_tag', help="tag of the telegram bot used for testing. Include the '@' character")
    parser.add_argument('--test_token', help="token for the telegram bot used for testing")

    # Other
    parser.add_argument('-p', '--path', help="path of the setting file (default: %(default)s)", default="config/settings.yaml")
    return parser


def check_args(args: dict):
    """Makes sure combination of args passed is valid

    Args:
        args (dict): the args passed by the user
    """
    if args['webhook'] and not args['urlwebhook']:
        print("If webhook is enabled, an urlwebhook must be provided")
        sys.exit(2)
    if args['remote'] and not args['database']:
        print("If remote is enabled, an access point to the database must be provided")
        sys.exit(2)

def main():
    """Main function
    """
    parser = create_argparser()
    args = vars(parser.parse_args())
    check_args(args)

    try:
        with open(args['path'], "r") as yaml_file:
            config_map = yaml.safe_load(yaml_file)
    except FileNotFoundError as e:
        print(e)
        sys.exit(2)

    config_map['token'] = args['token']
    config_map['data']['remote'] = args['remote']
    config_map['data']['db_url'] = args['database']
    config_map['webhook']['enabled'] = args['webhook']
    config_map['webhook']['url'] = args['urlwebhook']

    config_map['meme']['group_id'] = args['group_id']
    config_map['meme']['channel_id'] = args['channel_id']
    config_map['meme']['channel_group_id'] = args['channel_group_id']

    config_map['test']['api_id'] = args['test_api_hash']
    config_map['test']['api_hash'] = args['test_api_id']
    config_map['test']['session'] = args['test_session']
    config_map['test']['tag'] = args['test_tag']
    config_map['test']['token'] = args['test_token']


    with open(args['path'], "w") as yaml_file:
        yaml.dump(config_map, yaml_file)


if __name__ == "__main__":
    main()
