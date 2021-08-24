import time
from infi.systray import SysTrayIcon
import threading
import requests
from urllib3.exceptions import MaxRetryError

from node import config

should_connect = True
is_connected = False


class Client:

    def __init__(self):
        menu_options = (
            ("Connect", None, Client.connect),
            ("Disconnect", None, Client.disconnect)
        )

        systray = SysTrayIcon(icon='image.ico', hover_text='RoScraper Node', menu_options=menu_options)
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
                    requests.get(config.server + 'ping')
                    print("Connection Successful")
                    systray.update(icon='connected.ico')

                except:
                    print("Connection Error")
                    systray.update(icon='disconnected.ico')

            time.sleep(config.online_check_delay)

    @staticmethod
    def connect(systray):
        global should_connect
        should_connect = True
        print('Connecting')
        systray.update(icon='default.ico')

    @staticmethod
    def disconnect(systray):
        global should_connect
        should_connect = False
        print('Disconnected')
        systray.update(icon='disconnected.ico')
