from termcolor import colored
from datetime import datetime
from typing import List
import wShellCmd
import config
import model
import time


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
    print(colored("Estimated time: 30 seconds", "blue"))
    # Getting ping of server list, and put it back in list of ping as ping_result
    # Will use to having server_status as network status
    ping_result = []
    for ip in server:
        ping = ps_cmd.get_ping(ip)  # return 0 or 1
        ping_result.append(ping)

    print(colored("Ping completed!", "green"))
    # Main init server in collection by real data.
    for idx, ip in enumerate(server):
        try:
            init_server = {
                "ip": ip,
                "server_status": ping_result[idx],
                "service_status": 1 if ping_result[idx] == 1 else 0,
                "date_time": int(datetime.now().timestamp()),
            }

            insert_id = m_client.init_server_document(
                server_document_initiation=init_server
            )
            print(colored(f"Server Successfully init! objID: {insert_id}", "green"))
        except:
            print(colored("Error in initialize server document in collection.", "red"))


def server_specification(system_name):
    """To Specific server name for getting index of that this function will help us.

    Master => 0
    Slave1 => 1
    Slave2 => 2
    I can use match like switch case in other lang, but we use python 3.7 and i think
    it would not work.
    """
    if system_name == "master" or system_name == "Master":
        return 0
    elif system_name == "slave1" or system_name == "Slave1":
        return 1
    elif system_name == "slave2" or system_name == "Slave2":
        return 2


def define_server_priority(index: int):
    """Define server priority.

    It's very important to have first, second and third ip address for priority of getting ping
    and set to db if ping, one of them was 0, that means this computer had leaved network.
    in other look, to assign the flag to which server? which server is master?
    This function will return two node index for getting value by index of them, nodes is not important what is slave or what is master
    but with that we can know which system can be master in the process flow.
    """
    p1: int  # System 1 can be master or other
    p2: int

    if index == 0:
        p1 = index + 1
        p2 = p1 + 1
    elif index == 1:
        p1 = index - 1
        p2 = index + 1
    elif index == 2:
        p1 = index - 1
        p2 = p1 - 1

    return {"dev1": p1, "dev2": p2}


def slv(ip: List, self_system: str, service_name: str):
    """Slave activator

    When it will work? and How?
    All servers in actual mode are slave. in slave function we will check service_status
    value of this server (we know with IP of that) until their value go to 1 to be master in process.
    Programme will perform that in several of the time to get 1 from service_status value from
    related document. if value was 1, this process will jump from to master function activator.
    """
    mongo_client = model.MongoDB(config.main_config["db"]["conn_string"])

    # Check server_specification function for more detail
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

    # When election is prepared, we will start the service as master of all slaves.
    master(system_index, ip, service_name, self_system)


def master(
    self_system_index: int, server_ip: List, service_name: str, self_system: str
):
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
    m_client = model.MongoDB(config.main_config["db"]["conn_string"])
    shell = wShellCmd.PowerShellCmd()

    while 1:
        # To getting status of specific service
        local_machine_service_status = shell.run(
            f"Get-Service -name {service_name} | select -First 1 -Expand Status"
        )

        if local_machine_service_status == "Stopped":
            """What Happend if service status was Stopped?

            It's not problem, it will put her service_status to 0, and will get ping of
            server slave1 and slave2, if server slave1 or slave2 was available in network
            priority is first by Server Slave1 then Slave2. if our assume was server 1 master.
            But in any situation if our master was slave1 (10.99.0.14), what will happen?
            I implemented this function as define_server_priority if our servers was 3.
            In the future i will update that with any number of servers.
            """
            # Dethrone the score of this server and and assign score to another servers.
            m_client.update_server_status(
                server_ip=server_ip[self_system_index],
                update_value={"service_status": 0},
            )

            # Checking return value of ping other servers as slave.
            # Getting priority function.
            server_priority = define_server_priority(index=self_system_index)
            # Ensure for our network computer
            ping_result_slave1 = shell.get_ping(server_ip[server_priority["dev1"]])
            ping_result_slave2 = shell.get_ping(server_ip[server_priority["dev2"]])

            # Assign flag to new master.
            if ping_result_slave1 == 1:
                # Active master feature for this computer.
                m_client.update_server_status(
                    server_ip=server_ip[server_priority["dev1"]],
                    update_value={"service_status": 1},
                )
                break
            elif ping_result_slave2 == 1:
                # Active master feature for this computer.
                m_client.update_server_status(
                    server_ip=server_ip[server_priority["dev2"]],
                    update_value={"service_status": 1},
                )
                break
            else:
                # We can log this to system log (Syslog).
                print(
                    "request time out for all machines, checking your server network."
                )
                break

        time.sleep(config.time_wating)

    """ why we need to go back slv activation function?
    
    In order to having infinite loop system, that look like a automatic process.
    If any system Dethrone the score of mastering, we need to new machine to be master.
    So if master machine goes off from mastering. this machine will be slave, so will be call 
    slv activation function.
    """

    slv(server_ip, self_system, service_name)
