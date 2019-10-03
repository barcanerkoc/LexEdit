import json
from pathlib import Path
import re
import importlib
import sys
import os

import requests

from src import morphologicalAnalysis
from src.session import Session


class Data:

    def __init__(self, username):

        self.dictPath = str(Path(__file__).parents[1]) + "\\Data\\Dictionary.json"
        self.analyzerURL = "http://ddil.isikun.edu.tr/morturws/"
        self.POSPyPath = ""
        self.suffixesPyPath = ""
        self.lastRegex = ""
        self.usersFolderPath = self.getUsersFolderPath()

        self.session = Session(username)

        with open(self.dictPath, "r", encoding="utf8") as file:
            self.data = json.load(file)

    @classmethod
    def setUsersFolderPath(cls, path):

        with open(str(Path(__file__).parents[1]) + "\\init.json", "r+", encoding="utf8") as initFile:
            init = json.load(initFile)
            init["usersFolderPath"] = path
            initFile.seek(0)
            initFile.truncate(0)
            json.dump(init, initFile, ensure_ascii=False, indent=2)

    @classmethod
    def getUsersFolderPath(cls):

        with open(str(Path(__file__).parents[1]) + "\\init.json", "r", encoding="utf8") as initFile:
            init = json.load(initFile)

            if len(init["usersFolderPath"]):
                return init["usersFolderPath"]
            else:
                return str(Path(__file__).parents[1]) + "\\Users\\"

    def loadData(self):

        with open(self.dictPath, "r", encoding="utf8") as file:
            self.data = json.load(file)

    def search(self, regex):

        try:
            re.compile(regex)
        except re.error:
            return ["error"], [""]

        self.lastRegex = regex

        regData = []
        for x in range(len(self.data)):

            lemma = self.data[x]["lemma"]
            if re.search(regex, lemma):
                regData.append(lemma)

        addedRoots = []

        with open(self.usersFolderPath + self.session.user.username + "\\Session Files\\Last Session\\All Added Roots.json", "r", encoding="utf8") as allAddedFile:
            allAddedJSON = json.load(allAddedFile)

            for x in range(len(allAddedJSON[0])):

                lemma = allAddedJSON[0][x]["lemma"]
                if re.search(regex, lemma):
                    addedRoots.append(lemma)

        if os.stat(self.usersFolderPath + self.session.user.username + "\\Session Files\\Current Session\\Added Roots.json").st_size:

            with open(self.usersFolderPath + self.session.user.username + "\\Session Files\\Current Session\\Added Roots.json", "r", encoding="utf8") as AddedFile:
                AddedJSON = json.load(AddedFile)

                for x in range(len(AddedJSON[0])):

                    lemma = AddedJSON[0][x]["lemma"]
                    if re.search(regex, lemma):
                        addedRoots.append(lemma)

        deletedLemmas = []

        with open(self.usersFolderPath + self.session.user.username + "\\Session Files\\Last Session\\All Deleted Lemmas.json", "r", encoding="utf8") as allDeletedFile:
            allDeletedJSON = json.load(allDeletedFile)

            for x in range(len(allDeletedJSON[0])):

                lemma = allDeletedJSON[0][x]["lemma"]
                if re.search(regex, lemma):
                    deletedLemmas.append(lemma)

        if os.stat(self.usersFolderPath + self.session.user.username + "\\Session Files\\Current Session\\Deleted Lemmas.json").st_size:

            with open(self.usersFolderPath + self.session.user.username + "\\Session Files\\Current Session\\Deleted Lemmas.json", "r", encoding="utf8") as DeletedFile:
                DeletedJSON = json.load(DeletedFile)

                for x in range(len(DeletedJSON[0])):

                    lemma = DeletedJSON[0][x]["lemma"]
                    if re.search(regex, lemma):
                        deletedLemmas.append(lemma)

        return regData, addedRoots, deletedLemmas

    def getCurrentLemmaDef(self, lemma):

        defData = []
        for x in range(len(self.data)):

            if lemma == self.data[x]["lemma"]:

                for y in range(len(self.data[x]["homonyms"])):

                    defaultPOS = self.POSMapper2(self.data[x]["homonyms"][y]["default_pos"])

                    senseDefData = []
                    senses = self.data[x]["homonyms"][y]["senses"]
                    for z in range(len(senses)):

                        if defaultPOS == self.POSMapper2(senses[z]["pos"]):
                            senseDefData.append(("-", senses[z]["gloss"]))
                        else:
                            senseDefData.append((self.POSMapper2(senses[z]["pos"]), senses[z]["gloss"]))

                    defData.append((defaultPOS, senseDefData))

        return defData

    def getSelectedRootDef(self, rootAndPOS):

        root = rootAndPOS.split("\t")[0]
        POS = self.POSMapper(rootAndPOS.split("\t")[1])

        defData = []
        temp = self.getCurrentLemmaDef(root)
        for x in range(len(temp)):

            if temp[x][0] == POS:
                defData.append(temp[x])

        return defData

    def getMorphologicalAnalysis(self, lemma):

        if not self.checkInternetConnection():
            return ""

        morphs = []
        if len(self.POSPyPath) > 0:
            sys.path.append(self.POSPyPath[:self.POSPyPath.rfind("/")])
            customPOSPy = importlib.import_module(self.POSPyPath[self.POSPyPath.rfind("/") + 1:-3])
            morphs = customPOSPy.getMorphologicalAnalysis(self, lemma, self.analyzerURL)
        else:
            morphs = morphologicalAnalysis.getMorphologicalAnalysis(self, lemma, self.analyzerURL)

        return morphs

    # Sözlük ile analizör arasında POSTag eşleşmesi üzerine
    def POSMapper(self, POS):

        return{
            "<NOM>": "N",
            "<VS>": "V",
            "<PRED>": "Pred",
            "<NUM>": "Num",
            "<POSTP>": "Postp",
            "<INTERJ>": "Interj"
        }.get(POS, "NoN")

    # Sözlükte bulunan def_pos, pos yapıları üzerine
    def POSMapper2(self, POS):

        if POS is None:
            return "NoN"

        if "a." in POS:
            return "N"
        elif "sf." in POS:
            return "N" # Adj
        elif "zf." in POS:
            return "Adv"
        elif "bağ." in POS:
            return "Conj"
        elif "zm." in POS:
            return "Pnon"
        elif "e." in POS:
            return "Postp"
        elif any(pos in POS for pos in ["mec.", "tkz.", "esk.", "ruh b.", "mat.", "hkr.", "tic.", "ed.", "din b.", "tar.", "tek.", "fiz."]):
            return "?"
        else:
            return "V"

    def setDefaultPreferences(self):

        self.dictPath = str(Path(__file__).parents[1]) + "\\Data\\Dictionary.json"
        self.analyzerURL = "http://ddil.isikun.edu.tr/morturws/"
        self.POSPyPath = ""
        self.suffixesPyPath = ""

    def addRoot(self, root, POSTag):

        addedRootsFile = open(self.usersFolderPath + self.session.user.username + "\\Session Files\\Current Session\\Added Roots.json", "a", encoding="utf8")
        addedRootsFile.write(root + "\t" + POSTag + "\n")

    def getDeletedLemmasJSON(self, lemma):

        for x in range(len(self.data)):
            if lemma == self.data[x]["lemma"]:
                return self.data[x]

    def getAddedRoots(self):

        addedRootsFile = open(self.usersFolderPath + self.session.user.username + "\\Session Files\\Current Session\\Added Roots.json", "r", encoding="utf8")

    def getDeletedLemmas(self):

        deletedLemmasFile = open(self.usersFolderPath + self.session.user.username + "\\Session Files\\Current Session\\Deleted Lemmas.json", "w", encoding="utf8")

    @classmethod
    def checkInternetConnection(cls):

        url = "http://ddil.isikun.edu.tr/mortur/"
        timeout = 5
        try:
            _ = requests.get(url, timeout=timeout)
            return True
        except requests.ConnectionError:
            return False

    @classmethod
    def intToRomanNumeral(cls, num):

        return {
            1: "I",
            2: "II",
            3: "III",
            4: "IV",
            5: "V",
            6: "VI",
            7: "VII",
            8: "VIII",
            9: "IX"
        }.get(num, "X")
