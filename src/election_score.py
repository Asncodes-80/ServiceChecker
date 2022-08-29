from typing import List
import time

from pymongo.message import update
import config
import model
import ps_shell


def server_specification(system_name: str):
    """To Specific server name for getting index of that this function will help us.

    Master => 0
    Slave1 => 1
    Slave2 => 2
    I can use match like switch case in other lang, but we use python 3.7 and i think
    it would not work.
    """
    if system_name.lower() == "master":
        return 0

    if system_name.lower() == "slave1":
        return 1

    if system_name.lower() == "slave2":
        return 2

    return None


def define_server_priority(index: int):
    """Define server priority.

    It's very important to have first, second and third ip address for priority of getting ping
    and set to db if ping, one of them was 0, that means this computer had leaved network.
    in other look, to assign the flag to which server? which server is master?
    This function will return two node index for getting value by index of them, nodes is not important what is slave or what is master
    but with that we can know which system can be master in the process flow.
    """
    main_priority: int  # System 1 can be master or other
    secondary_priority: int

    if index == 0:
        main_priority = index + 1
        secondary_priority = main_priority + 1
    elif index == 1:
        main_priority = index - 1
        secondary_priority = index + 1
    elif index == 2:
        main_priority = index - 1
        secondary_priority = main_priority - 1

    return {"dev1": main_priority, "dev2": secondary_priority}


def net_problem_check(self_system_index: int, server_ip: List):
    """Checking servers from the network problem.

    I will expline this after write that.
    """
    # Initialize our important classes
    shell = ps_shell.PowerShellCmd()
    mongo_client = model.MongoDB(config.main_config["db_config"]["conn_string"])

    # Getting other server ip address like this:
    # If this computer was slave1 ~ 14 we will have this ip list [13, 15].
    # For ensure from we have ping of 13 or 15 we need from ping of those.
    server_ip: list = server_ip.copy()
    other_server_ip: list = server_ip.remove(server_ip[self_system_index])
    ping_sys1: bool = shell.get_ping(other_server_ip[0])
    ping_sys2: bool = shell.get_ping(other_server_ip[1])

    if ping_sys1 or ping_sys2:
        # Getting ip of active machine that has service_status value 1
        master_server: str = mongo_client.find_obj({"service_status", 1})["ip"]
        # Get ping master_server if was not able
        ping_master_server: bool = shell.get_ping(master_server)
        # If ping_master_server was false, we need
        if not ping_master_server:
            # Getting active master machine for
            slave_machines_document: list = mongo_client.find_obj({"service_status": 0})
            # Set service_status of master machine to 0 and server_status will be 0
            # Because it left the network!
            mongo_client.update_server_status(
                server_ip=master_server, update_value={"service_status": 0}
            )
            mongo_client.update_server_status(
                server_ip=master_server, update_value={"server_status": 0}
            )

            live_machines_ip = [
                slave_machines_document[0]["ip"],
                slave_machines_document[1]["ip"],
            ]
            live_machines_priority = [
                slave_machines_document[0]["priority"],
                slave_machines_document[1]["priority"],
            ]

            if live_machines_priority[0] < live_machines_priority[1]:
                mongo_client.update_server_status(
                    server_ip=live_machines_ip[0], update_value={"service_status": 1}
                )
            else:
                mongo_client.update_server_status(
                    server_ip=live_machines_ip[1], update_value={"service_status": 1}
                )


def slv(servers_ip: List, self_system: str, service_name: str):
    """Slave activator

    When it will work? and How?
    All servers in actual mode are slave. in slave function we will check service_status
    value of this server (we know with IP of that) until their value go to 1 to be master in process.
    Programme will perform that in several of the time to get 1 from service_status value from
    related document. if value was 1, this process will jump from to master function activator.
    """
    print("slave activator function started!")
    mongo_client = model.MongoDB(config.main_config["db_config"]["conn_string"])

    # Check server_specification function for more detail
    system_index = server_specification(self_system)
    shell = ps_shell.PowerShellCmd()

    while 1:
        self_check_service = mongo_client.find_obj({"ip": servers_ip[system_index]})[
            "service_status"
        ]

        # Checking if election for this is prepared
        if self_check_service == 1:
            shell.run(f"start-service {service_name}")
            break

        # Checking system if someone was down
        net_problem_check(self_system_index=system_index, server_ip=servers_ip)

        time.sleep(config.time_wating)

    # When election is prepared, we will start the service as master of all slaves.
    master(system_index, servers_ip, service_name, self_system)


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

    What Happend if service status was Stopped?
    It's not problem, it will put her service_status to 0, and will get ping of
    server slave1 and slave2, if server slave1 or slave2 was available in network
    priority is first by Server Slave1 then Slave2. if our assume was server 1 master.
    But in any situation if our master was slave1 (10.99.0.14), what will happen?
    I implemented this function as define_server_priority if our servers was 3.
    In the future i will update that with any number of servers.
    """
    print("Master activator function started!")
    m_client = model.MongoDB(config.main_config["db_config"]["conn_string"])
    shell = ps_shell.PowerShellCmd()

    while 1:
        # To getting status of specific service
        local_machine_service_status = shell.run(
            f"Get-Service -name {service_name} | select -First 1 -Expand Status"
        )
        print(local_machine_service_status)

        if local_machine_service_status == "Stopped":
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

            if ping_result_slave2 == 1:
                # Active master feature for this computer.
                m_client.update_server_status(
                    server_ip=server_ip[server_priority["dev2"]],
                    update_value={"service_status": 1},
                )
                break

            # Before of break we can log that this server was not able to perform service running.
            break

        time.sleep(config.time_wating)

    # why we need to go back slv activation function?
    # In order to having infinite loop system, that look like a automatic process.
    # If any system Dethrone the score of mastering, we need to new machine to be master.
    # So if master machine goes off from mastering. this machine will be slave, so will be call
    # slv activation function.
    slv(server_ip, self_system, service_name)
