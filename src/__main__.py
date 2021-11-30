from termcolor import colored
from datetime import datetime
from typing import List
import wShellCmd
import argparse
import config
import model
import time

parser = argparse.ArgumentParser()

# Getting ip list of servers from the pshell
parser.add_argument(
    "-ipl",
    "--ip_list",
    help="IP Address list is your priority list. [master, slave1, slave2]",
)

# Getting self machine name (master|slave1|slave2)
parser.add_argument(
    "-s",
    "--self",
    help="Initialize servers system into collection, only yes or no",
)

# Getting self machine name (master|slave1|slave2)
parser.add_argument(
    "-serv",
    "--service_name",
    help="Service name for starting or stopping on the windows ps",
)

# Getting --init as server document initializer
parser.add_argument(
    "-init",
    "--init_servers",
    help="Initialize servers system into collection, only yes or no",
)
args = parser.parse_args()


def init_server(server: List):
    """This init only for initialize server data on the collection document.

    only one arg, arg is list of server IP, please use proper priority, because it's
    very important to have first, second and third ip address.
    first ip will by default master and service_status will 1.
    ["10.99.0.13", "10.99.0.14", "10.99.0.15"]
    """
    ps_cmd = wShellCmd.PowerShellCmd()
    m_client = model.MongoDB(config.main_config["db"]["conn_string"])

    print(colored("Wait for getting ping, to ensure connection is normal...", "blue"))

    # Getting ping of server list, and put it back in list of ping as ping_result
    # Will use to having server_status as network status
    ping_result = []
    for ip in server:
        ping = ps_cmd.get_ping(ip)  # return 0 or 1
        ping_result.append(ping)

    print(colored("Ping completed!", "green"))

    # Main init server in collection by real data.
    for idx, ip in enumerate(server):
        init_server = {
            "ip": ip,
            "server_status": ping_result[idx],
            "service_status": 1 if ping_result[idx] == 1 else 0,
            "date_time": int(datetime.now().timestamp()),
        }
        m_client.init_server_document(server_document_initiation=init_server)


def server_specification(system_name):
    """To Specific server name for getting index of that this function will help us.

    Master => 0
    Slave1 => 1
    Slave2 => 2
    I can use match like switch case in other lang, but we use python 3.7 and i think
    it would not work.
    """
    if system_name == "master":
        return 0
    elif system_name == "slave1":
        return 1
    elif system_name == "slave2":
        return 2


def slv(ip: List, self_system: str, service_name: str):
    """Slave activator

    When it will work? and How?
    All servers in actual mode are slave. in slave function we will check service_status
    value of this server (we know with IP of that) until their value go to 1 to be master in process.
    Programme will perform that in several of the time to get 1 from service_status value from
    related document. if value was 1, this process will jump from to master function activator.
    """
    mongo_client = model.MongoDB(config.main_config["db"]["conn_string"])
    system_index = server_specification(self_system)
    shell = wShellCmd.PowerShellCmd()

    while 1:
        self_check_service = mongo_client.get_statuses(
            ip[system_index], "service_status", 1
        )[0]["service_status"]

        # Checking if election for this is prepared
        if self_check_service == 1:
            shell.run(f"start-service {service_name}")
            break

        time.sleep(config.time_wating)

    master(ip, service_name)


def master(server_ip: List, service_name: str):
    """Master activator it long, so quit and read withour stress.

    When it will work? and How?
    After process jumped into master activator function, in several time will check status of service
    if was stopped, it will works hard with this condition:
    if status of checking_service was stopped, go back to document collection of related server and change
    value of service_status to 0. that means this server can't work with this service. okay and next, will get
    ping of slave1 and slave2, if any one of that was not True, it will set in related server document, value 0 into server_status
    After that will go to our condition, this condition will be a priority of running service on which system. if ping of slave 1 was
    true will change service_status of slave1 to 1 for continue the service on that server. or if slave1 wasn't able to perform the service
    because result of the Ping was False and will jump into next condition, that perform starting service on slave2, if slave2 wasn't able to
    perform service running major, it will back to loop, util one of the server was able to perform service running.
    """
    shell = wShellCmd.PowerShellCmd()

    while 1:
        local_machine_service_status = shell.run(
            f"Get-Service -name {service_name} | select -First 1 -Expand Status"
        )

        if local_machine_service_status == "Stopped":
            """"""
            # Dethrone the score of this server and and assign score to another servers
            # Updating document
            

            # Checking return value of ping other servers

            # Priority of running service on which server

        time.sleep(config.time_wating)


if args.ip_list and args.init_servers == "yes":
    init_server(server=args.ip_list)
elif args.ip_list and args.self and args.service_name and args.init_servers == "no":
    slv(ip=args.ip_list, self_system=args.self, service_name=args.service_name)
else:
    print("Complete the options. you're require to enter server IP list")
