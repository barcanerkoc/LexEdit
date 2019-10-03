from pathlib import Path
import json
import hashlib


class User:

    def __init__(self, username):

        self.username = username

    @classmethod
    def login(cls, username, password):

        if username == "defaultUser" and password == "12345":
            return True

        with open(str(Path(__file__).parents[1]) + "\\init.json", "r+", encoding="utf8") as initFile:
            init = json.load(initFile)

            if len(init["usersFolderPath"]):
                with open(init["usersFolderPath"] + "\\Users.json", "r", encoding="utf8") as usersFile:
                    users = json.load(usersFile)

            else:
                with open(str(Path(__file__).parents[1]) + "\\Users\\Users.json", "r", encoding="utf8") as usersFile:
                    users = json.load(usersFile)

        for x in range(len(users)):

            if users[x]["username"] == username and hashlib.md5((users[x]["salt"] + password).encode()).hexdigest() == users[x]["password"]:
                return True

        return False
