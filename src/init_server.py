from datetime import datetime
from typing import List
from termcolor import colored
import config
import model
import ps_shell


def init_server(server: List):
    """This init only for initialize server data on the collection document.

    only one arg, arg is list of server IP, please use proper priority, because it's
    very important to have first, second and third ip address.
    first ip will by default master and service_status will 1.
    ["10.99.0.13", "10.99.0.14", "10.99.0.15"]
    """
    ps_cmd = ps_shell.PowerShellCmd()
    m_client = model.MongoDB(config.main_config["db_config"]["conn_string"])

    print(colored("Wait for getting ping, to ensure connection is normal...", "blue"))
    print(colored("Estimated time: 30 seconds", "blue"))
    # Getting ping of server list, and put it back in list of ping as ping_result
    # Will use to having server_status as network status
    ping_result = []
    for string_ip_ad in server:
        ping = ps_cmd.get_ping(string_ip_ad)  # return 0 or 1
        ping_result.append(ping)

    print(colored("Ping completed!", "green"))
    # Main init server in collection by real data.
    for idx, ip_ad in enumerate(server):
        try:
            # This section will find document if before exist in collection
            # And prevent document repeat
            exist_document = m_client.find_obj(key="ip", value=ip_ad)
            if not exist_document:
                init_server_document = {
                    "ip": ip_ad,
                    "server_status": 1 if ping_result[idx] else 0,
                    "service_status": 1 if idx == 0 else 0,
                    "date_time": int(datetime.now().timestamp()),
                }

                insert_id = m_client.init_server_document(
                    server_document_initiation=init_server_document
                )
                print(colored(f"Server Successfully init! objID: {insert_id}", "green"))
            else:
                print(colored(f"Servers document exits in Collection", "red"))

        except Exception as init_server_err:
            print(
                colored(
                    f"Error in initialize server document in collection.\n{init_server_err}",
                    "red",
                )
            )
