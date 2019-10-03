from pathlib import Path
from shutil import copyfile
import os

from src.admin import Admin
from src.annotator import Annotator
import json




class Session:

    def __init__(self, username):

        if username == "admin":
            self.user = Admin(username)
            self.user.setPath(self.getUsersFolderPath())
        else:
            self.user = Annotator(username)

        # Fileda tut ordan oku init ederken
        self.initFilePath = ""
        self.collapsedSensesFilePath = ""
        self.usersFolderPath = self.getUsersFolderPath()

        self.addedRoots = []
        self.deletedLemmas = []
        self.deletedLemmasOnlyLemma = []
        self.collapsedSenses = {}

    @classmethod
    def getUsersFolderPath(cls):

        with open(str(Path(__file__).parents[1]) + "\\init.json", "r", encoding="utf8") as initFile:
            init = json.load(initFile)

            if len(init["usersFolderPath"]):
                return init["usersFolderPath"]
            else:
                return str(Path(__file__).parents[1]) + "\\Users\\"

    def setInitFilePath(self, usersFilePath):

        print()

    def setCollapsedSensesFilePath(self, usersFilePath):

        print()

    def loadLastSession(self):

        lastSessionFile = open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\init.json", "r", encoding="utf8")
        lastSessionInfo = json.load(lastSessionFile)

        if os.stat(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\Collapsed Senses.json").st_size:
            collapsedSensesFile = open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\Collapsed Senses.json", "r", encoding="utf8")
            self.collapsedSenses = json.load(collapsedSensesFile)

        return lastSessionInfo["lastRegex"], lastSessionInfo["lastSelectedLemma"]

    def addRoot(self, root, POSTag):

        if root in self.addedRoots:
            return

        if len(root):
            self.addedRoots.append([root, POSTag])  # Tuple yerine 2. list kullanılabilir

        addedRootsFile = open(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Added Roots.json", "w", encoding="utf8")
        jsonData = []
        for x in range(len(self.addedRoots)):
            jsonData.append(json.dumps(
                {
                    "homonyms":
                        [
                            {
                                "senses":
                                    [
                                        {
                                            "inferred_pos": self.addedRoots[x][1],
                                            "gloss": "",
                                            "pos": self.addedRoots[x][1],
                                            "example": ""
                                        }
                                    ],
                                "raw_gloss": "",
                                "lemma": self.addedRoots[x][0],
                                "default_pos": self.addedRoots[x][1]
                            }
                        ],
                    "lemma": self.addedRoots[x][0],
                }
            )
            )

        jsonObjects = [json.loads(s) for s in jsonData]
        jsonObjects2 = [jsonObjects, {"annotator": self.user.username}]

        json.dump(jsonObjects2, addedRootsFile, ensure_ascii=False, indent=2)

    def deleteLemma(self, lemma):

        if lemma in self.deletedLemmasOnlyLemma:
            return

        if len(lemma):
            self.deletedLemmasOnlyLemma.append(lemma)

        deletedLemmasFile = open(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Deleted Lemmas.json", "w", encoding="utf8")

        jsonObjects = [self.deletedLemmas, {"annotator": self.user.username}]

        json.dump(jsonObjects, deletedLemmasFile, ensure_ascii=False, indent=2)

    def endOfSession(self, lastRegex, lastSelectedLemma):

        self.updateLastSessionJSONs()
        self.updateAllJSONs()

        open(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Added Roots.json", "w", encoding="utf8").close()
        open(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Deleted Lemmas.json", "w", encoding="utf8").close()

        if len(self.collapsedSensesFilePath):
            collapsedSensesFile = open(self.collapsedSensesFilePath, "r+", encoding="utf8")
        else:
            collapsedSensesFile = open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\Collapsed Senses.json", "w", encoding="utf8")

        json.dump(
            self.collapsedSenses,
            collapsedSensesFile,
            ensure_ascii=False,
            indent=2
        )

        if len(self.initFilePath):
            initFile = open(self.initFilePath, "w", encoding="utf8")
        else:
            initFile = open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\init.json", "w", encoding="utf8")

        json.dump(
            {
                "lastRegex": lastRegex,
                "lastSelectedLemma": lastSelectedLemma
            },
            initFile,
            ensure_ascii=False,
            indent=2
        )

    def updateLastSessionJSONs(self):

        copyfile(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Added Roots.json", self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\Added Roots.json")
        copyfile(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Deleted Lemmas.json", self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\Deleted Lemmas.json")

    def updateAllJSONs(self):

        if os.stat(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Added Roots.json").st_size:
            addedRootsFile = open(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Added Roots.json", "r", encoding="utf8")

            with open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\All Added Roots.json", "r", encoding="utf8") as allAddedFile:
                allAddedJSON = json.load(allAddedFile)
            allAddedJSON[0].extend(json.load(addedRootsFile)[0])

            with open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\All Added Roots.json", "w", encoding="utf8") as allAddedFile:
                json.dump(allAddedJSON, allAddedFile, ensure_ascii=False, indent=2)

        if os.stat(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Deleted Lemmas.json").st_size:
            deletedLemmasFile = open(self.usersFolderPath + self.user.username + "\\Session Files\\Current Session\\Deleted Lemmas.json", "r", encoding="utf8")

            with open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\All Deleted Lemmas.json", "r", encoding="utf8") as allDeletedFile:
                allDeletedJSON = json.load(allDeletedFile)
            allDeletedJSON[0].extend(json.load(deletedLemmasFile)[0])

            with open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\All Deleted Lemmas.json", "w", encoding="utf8") as allDeletedFile:
                json.dump(allDeletedJSON, allDeletedFile, ensure_ascii=False, indent=2)

    def undoAdd(self, root):

        check = False
        for x in range(len(self.addedRoots)):
            if self.addedRoots[x][0] == root:
                self.addedRoots.pop(x)
                check = True
                break

        if check:

            self.addRoot("", "")

        else:

            with open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\All Added Roots.json", "r", encoding="utf8") as allAddedFile:
                allAddedJSON = json.load(allAddedFile)

            for x in range(len(allAddedJSON[0])):
                if allAddedJSON[0][x]["lemma"] == root:
                    del allAddedJSON[0][x]
                    break

            with open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\All Added Roots.json", "w", encoding="utf8") as allAddedFile:
                json.dump(allAddedJSON, allAddedFile, ensure_ascii=False, indent=2)

    def undoDelete(self, lemma):

        if lemma in self.deletedLemmasOnlyLemma:

            self.deletedLemmasOnlyLemma.remove(lemma)

            for x in range(len(self.deletedLemmas)):

                if self.deletedLemmas[x]["lemma"] == lemma:
                    self.deletedLemmas.pop(x)
                    break

            self.deleteLemma("")

        else:

            with open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\All Deleted Lemmas.json", "r", encoding="utf8") as allDeletedFile:
                allDeletedJSON = json.load(allDeletedFile)

            for x in range(len(allDeletedJSON[0])):
                if allDeletedJSON[0][x]["lemma"] == lemma:
                    del allDeletedJSON[0][x]
                    break

            with open(self.usersFolderPath + self.user.username + "\\Session Files\\Last Session\\All Deleted Lemmas.json", "w", encoding="utf8") as allDeletedFile:
                json.dump(allDeletedJSON, allDeletedFile, ensure_ascii=False, indent=2)
