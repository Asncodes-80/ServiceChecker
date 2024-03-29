import argparse
from termcolor import colored
import config
from election_score import slv
from init_server import init_server

parser = argparse.ArgumentParser()
# Process on the list of option in config file
for option in config.args_parser_options:
    parser.add_argument(
        option["name"],
        option["complete_name"],
        help=option["help"],
    )

args = parser.parse_args()


def convert_ip_list(ip_string: str):
    """Convert String ip to real list.

    To have list of ip as string value, user must enter list of that like this:
    "ip1 ip2 ip3" => ["ip1", "ip2", "ip3"]
    As i mention before, you must put space between ip.
    """
    return ip_string.split(" ")


if args.ip_list and args.building_name and args.init_servers.lower() == "yes":
    init_server(server=convert_ip_list(args.ip_list), building_name=args.building_name)
elif (
    args.ip_list
    and args.self
    and args.service_name
    and args.building_name
    and args.init_servers.lower() == "no"
):
    slv(
        servers_ip=convert_ip_list(args.ip_list),
        self_system=args.self,
        service_name=args.service_name,
    )
else:
    print(
        colored("Complete the options. you're require to enter server IP list", "red")
    )
