import os
from pathlib import Path
from random import randrange
from random import choices
import string
import json
import hashlib

from src.user import User


class Admin(User):

    def __init__(self, username):

        super().__init__(username)

        self.approvedAddedList = []
        self.approvedDeletedList = []

    def setPath(self, path):

        self.usersFolderPath = path

    def createUser(self, username, password):

        with open(self.usersFolderPath + "\\Users.json", "r+", encoding="utf8") as usersFile:
            users = json.load(usersFile)
            salt = ''.join(choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=randrange(6, 12)))
            k = json.dumps(
                {
                    "username": username,
                    "salt": salt,
                    "password": hashlib.md5((salt + password).encode()).hexdigest()
                }
            )

            users.append(json.loads(k))
            usersFile.seek(0)
            json.dump(users, usersFile, ensure_ascii=False, indent=2)

            if not os.path.exists(self.usersFolderPath + "\\" + username):

                os.makedirs(self.usersFolderPath + "\\" + username + "\\Session Files\\Current Session")
                os.makedirs(self.usersFolderPath + "\\" + username + "\\Session Files\\Last Session")
                open(self.usersFolderPath + username + "\\Session Files\\Current Session\\Added Roots.json", "w", encoding="utf8").close()
                open(self.usersFolderPath + username + "\\Session Files\\Current Session\\Deleted Lemmas.json", "w", encoding="utf8").close()
                open(self.usersFolderPath + username + "\\Session Files\\Last Session\\Added Roots.json", "w", encoding="utf8").close()
                open(self.usersFolderPath + username + "\\Session Files\\Last Session\\Deleted Lemmas.json", "w", encoding="utf8").close()
                open(self.usersFolderPath + username + "\\Session Files\\Last Session\\All Added Roots.json", "w", encoding="utf8").close()
                open(self.usersFolderPath + username + "\\Session Files\\Last Session\\All Deleted Lemmas.json", "w", encoding="utf8").close()
                with open(self.usersFolderPath + username + "\\Session Files\\Last Session\\init.json", "w", encoding="utf8") as initFile:
                    json.dump(
                        {
                            "lastRegex": "",
                            "lastSelectedLemma": ""
                        },
                        initFile,
                        ensure_ascii=False,
                        indent=2
                    )
                    initFile.close()

    def getAllAnnotatorData(self):

        usersData = []
        for directory in os.listdir(self.usersFolderPath):

            if directory == "Users.json" or directory == "Admin":
                continue

            addedRoots = []
            deletedLemmas = []

            with open(self.usersFolderPath + directory + "\\Session Files\\Last Session\\All Added Roots.json", "r", encoding="utf8") as addedRootsFile:
                temp = json.load(addedRootsFile)
                for x in range(len(temp[0])):
                    addedRoots.append((temp[0][x]["lemma"], temp[0][x]["homonyms"][0]["default_pos"]))

            with open(self.usersFolderPath + directory + "\\Session Files\\Last Session\\All Deleted Lemmas.json", "r", encoding="utf8") as deletedLemmasFile:
                temp = json.load(deletedLemmasFile)
                for x in range(len(temp[0])):
                    deletedLemmas.append(temp[0][x]["lemma"])

            usersData.append((directory, addedRoots, deletedLemmas))

        return usersData

    def approveAddedRoot(self, rootAndPOS):

        self.approvedAddedList.append((rootAndPOS.split("\t")[0], rootAndPOS.split("\t")[1]))

    def approveDeletedLemma(self, lemma):

        self.approvedDeletedList.append(lemma)

    def createDictionary(self, dictName):

        if not len(dictName):
            return

        with open(str(Path(__file__).parents[1]) + "\\Data\\Dictionary.json", "r", encoding="utf8") as baseDictionary:
            baseDict = json.load(baseDictionary)

            with open(self.usersFolderPath + "\\Admin\\" + dictName + ".json", "w", encoding="utf8") as newDictionary:

                newDict = []
                for x in range(len(baseDict)):

                    hit = None
                    for y in range(len(self.approvedDeletedList)):

                        if self.approvedDeletedList[y] == baseDict[x]["lemma"]:
                            hit = self.approvedDeletedList[y]
                            break

                    if hit is not None:
                        self.approvedDeletedList.remove(hit)
                        continue

                    for y in range(len(self.approvedAddedList)):

                        if ord(self.approvedAddedList[y][0][0]) < ord(baseDict[x]["lemma"][0]) or len(self.approvedAddedList[y][0]) > len(baseDict[x]["lemma"]):
                            continue

                        check = True
                        if self.approvedAddedList[y][0][0] == baseDict[x]["lemma"][0]:

                            for charIndex in range(1, len(self.approvedAddedList[y][0])):

                                if ord(self.approvedAddedList[y][0][charIndex]) > ord(baseDict[x]["lemma"][charIndex]):
                                    check = False
                                    break

                                if ord(self.approvedAddedList[y][0][charIndex]) < ord(baseDict[x]["lemma"][charIndex]):

                                    temp = json.dumps(
                                        {
                                            "homonyms":
                                                [
                                                    {
                                                        "senses":
                                                            [
                                                                {
                                                                    "inferred_pos": self.approvedAddedList[y][1],
                                                                    "gloss": "",
                                                                    "pos": self.approvedAddedList[y][1],
                                                                    "example": ""
                                                                }
                                                            ],
                                                        "raw_gloss": "",
                                                        "lemma": self.approvedAddedList[y][0],
                                                        "default_pos": self.approvedAddedList[y][1]
                                                    }
                                                ],
                                            "lemma": self.approvedAddedList[y][0],
                                        }
                                    )

                                    newDict.append(json.loads(temp))

                                    check = False
                                    break

                            if check:

                                temp = json.dumps(
                                    {
                                        "homonyms":
                                            [
                                                {
                                                    "senses":
                                                        [
                                                            {
                                                                "inferred_pos": self.approvedAddedList[y][1],
                                                                "gloss": "",
                                                                "pos": self.approvedAddedList[y][1],
                                                                "example": ""
                                                            }
                                                        ],
                                                    "raw_gloss": "",
                                                    "lemma": self.approvedAddedList[y][0],
                                                    "default_pos": self.approvedAddedList[y][1]
                                                }
                                            ],
                                        "lemma": self.approvedAddedList[y][0],
                                    }
                                )

                                newDict.append(json.loads(temp))

                    newDict.append(baseDict[x])

                json.dump(newDict, newDictionary, ensure_ascii=False, indent=2)

    def temp(self):

        print("asdasd")

    def temp2(self):

        print("2222")


# k = Admin("admin")
# k.createUser("abc", "456")

