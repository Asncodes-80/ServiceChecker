import argparse
from termcolor import colored
import config
import election_score as election

parser = argparse.ArgumentParser()
# Process on the list of option in config file
for option in config.args_parser_options:
    parser.add_argument(
        option["name"],
        option["complete_name"],
        type=option["type"],
        help=option["help"],
    )

args = parser.parse_args()


def convert_ip_list(ip_string: str):
    return ip_string.split(" ")


if args.ip_list and args.init_servers == "yes":
    election.init_server(server=convert_ip_list(args.ip_list))
elif args.ip_list and args.self and args.service_name and args.init_servers == "no":
    election.slv(
        servers_ip=convert_ip_list(args.ip_list),
        self_system=args.self,
        service_name=args.service_name,
    )
else:
    print(
        colored("Complete the options. you're require to enter server IP list", "red")
    )
