import requests
import json
import time
import os
import sys
import colorama


class Network:

    # Returns un-formatted item meta-data from the Rolimons API
    @staticmethod
    def pull_item_meta():
        url = "https://www.rolimons.com/itemapi/itemdetails"
        response = requests.get(url)
        parsed_data = json.loads(response.text)
        return parsed_data

    # Returns un-formatted item data from the Rolimons API
    @staticmethod
    def pull_item_data(item_id):
        # Retrieve raw data
        url = "https://www.rolimons.com/item/" + item_id
        response = requests.get(url)
        return response.text

    @staticmethod
    def parse_hoarders(raw_data):
        # Declare keywords to search for
        hoards_keyword = "var hoards_data                    = "

        # Determine offsets
        hoards_json_start = raw_data.find(hoards_keyword) + len(hoards_keyword)

        # Declare empty variables for population
        hoards_raw_json = ""
        hoards_json_end = 0
        user_ids = []

        for char_location in range(len(raw_data)):
            if raw_data[char_location + hoards_json_start] == "}":
                hoards_json_end = char_location + hoards_json_start + 1
                break

        for char in range(hoards_json_start, hoards_json_end):
            hoards_raw_json += raw_data[char]

        hoards_json = json.loads(hoards_raw_json)

        for user_id in hoards_json["owner_ids"]:
            user_ids.append(user_id)

        return user_ids

    @staticmethod
    def parse_owners(raw_data):
        # Declare keywords to search for
        bc_copies_keyword = "var bc_copies_data                 = "

        # Determine offsets
        bc_copies_json_start = raw_data.find(bc_copies_keyword) + len(bc_copies_keyword)

        # Declare empty variables for population
        bc_copies_raw_json = ""
        bc_copies_json_end = 0
        user_ids = []

        for char_location in range(len(raw_data)):
            # LMAO THIS IS BAD-
            if raw_data[char_location + bc_copies_json_start]:
                if raw_data[char_location + bc_copies_json_start] == "}":
                    bc_copies_json_end = char_location + bc_copies_json_start + 1
                    break

        for char in range(bc_copies_json_start, bc_copies_json_end):
            bc_copies_raw_json += raw_data[char]

        bc_copies_json = json.loads(bc_copies_raw_json)

        for user_id in bc_copies_json["owner_ids"]:
            user_ids.append(user_id)

        return user_ids

    # Return the name of all items returned by the API
    @staticmethod
    def parse_item_names(parsed_data):
        item_names = []

        for item_id in parsed_data["items"]:
            item_names.append(parsed_data["items"][item_id][0])

        return item_names

    # Return the nickname of all items returned by the API
    @staticmethod
    def parse_item_nicknames(parsed_data):
        item_nicknames = []

        for item_id in parsed_data["items"]:
            item_nicknames.append(parsed_data["items"][item_id][1])

        return item_nicknames

    # Return the ID of all items returned by the API
    @staticmethod
    def parse_item_ids(parsed_data):
        item_ids = []

        for item_id in parsed_data["items"]:
            item_ids.append(item_id)

        return item_ids

    @staticmethod
    def pull_item_owners(parsed_data):
        pass


class Local:
    pass


# Provider agnostic interface for retrieving data in memory
class Data:
    pass


class UI:

    # Please end me this code is beyond cursed
    @staticmethod
    def intro():
        colorama.init()

        lines = [
            "      ______     ______     ______     ______     ______     ______     ______   ______     ______   ",
            "     /\  == \   /\  __ \   /\  ___\   /\  ___\   /\  == \   /\  __ \   /\  == \ /\  ___\   /\  == \\   ",
            "     \ \  __<   \ \ \/\ \  \ \___  \  \ \ \____  \ \  __<   \ \  __ \  \ \  _-/ \ \  __\   \ \  __<   ",
            "      \ \_\ \_\  \ \_____\  \/\_____\  \ \_____\  \ \_\ \_\  \ \_\ \_\  \ \_\    \ \_____\  \ \_\ \_\\   ",
            "       \/_/ /_/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_/\/_/   \/_/     \/_____/   \/_/ /_/   "
            ""
        ]

        UI.clear_top_line()

        for i in range(1, 11):
            print()

        for line in lines:
            UI.dramatic_print(line)
            print("")

        sys.stdout.write("\033[C\033[C\033[C")
        sys.stdout.flush()
        sys.stdout.write("\033[A\033[A\033[A\033[A\033[A\033[A+")
        sys.stdout.flush()
        UI.dramatic_print("-" * 97 + "+")

        for i in range(1, 6):
            print()
            sys.stdout.write("\033[C" * 101 + "|")
            sys.stdout.flush()
            time.sleep(0.01)

        print()
        sys.stdout.write("\033[C" * 101 + "+")
        sys.stdout.flush()

        for i in range(1, 98):
            sys.stdout.write("\033[D\033[D-")
            sys.stdout.flush()
            time.sleep(0.01)

        sys.stdout.write("\033[D\033[D+")
        sys.stdout.flush()
        time.sleep(0.01)

        for i in range(1, 6):
            print()
            sys.stdout.write("\033[A\033[A" + ("\033[C" * 3) + "|")
            sys.stdout.flush()
            time.sleep(0.01)

        for i in range(1, 7):
            print()

        sys.stdout.write("\033[C" * 41)

        UI.dramatic_print("RoScraper --- v0.01", 0.1)

        time.sleep(1)

        for i in range(1, 22):
            print()

    @staticmethod
    def dramatic_print(text, speed=0.01):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(speed)

    @staticmethod
    def clear_top_line():
        sys.stdout.write("\033[A")
        sys.stdout.flush()
        for i in range(100):
            sys.stdout.write(" ")
            sys.stdout.flush()
            time.sleep(0.01)


# Temporary hack
def pull_everything():
    print("Pulling item IDs...")
    parsed_data = Network.pull_item_meta()
    item_ids = Network.parse_item_ids(parsed_data)
    item_names = Network.parse_item_names(parsed_data)
    print("Successfully pulled " + str(len(item_ids)) + " item IDs!")
    print("-" * 20)
    time.sleep(0.1)
    for item_index in range(len(item_ids)):
        string = "Dumping user IDs for item " + item_names[item_index] + " (" + item_ids[item_index] + ")"
        print(string, end="")
        print(" " * (100 - len(string)), end="")
        print(" | " + str(item_index + 1) + " out of " + str(len(item_ids)))

        user_ids = None
        while user_ids is None:
            try:
                item_data = Network.pull_item_data(item_ids[item_index])
                user_ids = Network.parse_owners(item_data)
            except IndexError:
                print("Rate Limit - Retrying")
                time.sleep(10)

        with open("item_data/" + item_ids[item_index] + " - " + item_names[item_index].replace(":", " ").replace("?",
                                                                                                                 " "),
                  'a') as file:
            for user_id in user_ids:
                file.write(str(user_id) + "\n")
