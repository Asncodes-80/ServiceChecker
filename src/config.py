""" Config file 
For using app in any where with diffrent situation and value
"""
# This is main section of config file for starting the script
# All option of this script you must enter in terminal to getting correct feed from that.
args_parser_options = [
    {
        "name": "-ipl",
        "complete_name": "--ip_list",
        "type": str,
        "help": "IP Address list is your priority list. [master, slave1, slave2]",
    },
    {
        "name": "-s",
        "complete_name": "--self",
        "type": str,
        "help": "Initialize servers system into collection, only yes or no",
    },
    {
        "name": "-service",
        "complete_name": "--service_name",
        "type": str,
        "help": "Service name for starting or stopping on the windows ps",
    },
    {
        "name": "-init",
        "complete_name": "--init_servers",
        "type": str,
        "help": "Initialize servers system into collection, only yes or no",
    },
]

time_wating = 2

main_config = {
    "db": {
        "conn_string": "mongodb://188.213.64.78:1000/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false",
        "db_name": "Ayandeh_db",
        "collection_name": "election",
    },
}
