import requests


def getMorphologicalAnalysis(self, lemma, analyzerURL):

    response = requests.post(analyzerURL, json={"wordList": [lemma]})
    morphAnalysis = response.json()

    morphs = []

    for x in range(len(morphAnalysis["analyses"][0])):

        root = morphAnalysis["analyses"][0][x][:morphAnalysis["analyses"][0][x].find("<")]
        POSTag = morphAnalysis["analyses"][0][x][morphAnalysis["analyses"][0][x].find("<"):morphAnalysis["analyses"][0][x].find("><") + 1]
        rest = morphAnalysis["analyses"][0][x][morphAnalysis["analyses"][0][x].find("><") + 1:]

        morphs.append(("in-ter-mediate", root + "\t" + POSTag + "\t" + rest))

    return morphs

