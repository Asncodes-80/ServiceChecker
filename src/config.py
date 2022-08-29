""" Config file 
For using app in any where with diffrent situation and value
"""
# This is main section of config file for starting the script
# All option of this script you must enter in terminal to getting correct feed from that.
args_parser_options = [
    {
        "name": "-ipl",
        "complete_name": "--ip_list",
        "help": "IP Address list is your priority list. [master, slave1, slave2]",
    },
    {
        "name": "-s",
        "complete_name": "--self",
        "help": "This system is which one?",
    },
    {
        "name": "-service",
        "complete_name": "--service_name",
        "help": "Service name for starting or stopping on the windows ps",
    },
    {
        "name": "-b",
        "complete_name": "--building_name",
        "help": "Add building name for separating in DB",
    },
    {
        "name": "-init",
        "complete_name": "--init_servers",
        "help": "Initialize servers system into collection, only yes or no",
    },
]

time_wating = 2

main_config = {
    "db_config": {
        "conn_string": "mongodb://172.16.24.14:1000/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false",
        "db_name": "MCI_CPR_DB",
        "collection_name": "Servers",
    },
}
