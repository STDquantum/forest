# Q: How to use this file?
# A: 1. Fill the right English name in "treeInfo.json" as "nameEN".
#    2. Get new tree type pngs and so do its file name as "trees\pngs".
#       Fill in the file name as "nameFile".
#    3. Fill in the database name as "nameDatabase".
#    4. Get "seekrtech_l10n.db", paste it into "databases".
#    5. Run this file with "python treeNames.py",
#       and harvest all the information in "treeType.json"!
#
# Q: Something else I can do?
# A: 1. Run "getGrowthGif.py" and look through the growth phases
#       of every tree in "growth\GIF".

import json
import sqlite3
import os


def getTreeName():
    info = json.load(open("treeInfo.json", "r", encoding = "utf-8"))
    for key in info:
        cur = int(key)
        data[cur] = {}
        data[cur]["nameEN"] = info[key]["nameEN"] # read English name
        data[cur]["nameZH"] = ""        # reserve positions for Chinese name
        data[cur]["nameFR"] = ""        # reserve positions for France name
        data[cur]["nameFile"] = info[key]["nameFile"]
        data[cur]["nameDatabase"] = info[key]["nameDatabase"]


def getDescription():
    conn = sqlite3.connect(".\\databases\\seekrtech_l10n.db")
    c = conn.cursor()
    database = c.execute("SELECT key, locale, value FROM L10nEntity WHERE locale = 'en' OR locale = 'zh_CN' OR locale = 'fr'")
    conn.commit()
    info = [{} for i in range(3)]
    for key, locale, value in database:
        if locale == "en":
            info[0][key] = value
        elif locale == "zh_CN":
            info[1][key] = value
        elif locale == "fr":
            info[2][key] = value

    # Descriptions
    for i in data:
        try:
            name = data[i]["nameDatabase"] + "_description"
            data[i]["descriptionEN"] = info[0][name]
            data[i]["descriptionZH"] = info[1][name]
            data[i]["descriptionFR"] = info[2][name]
        except:
            continue

    # Chinese and France names
    for i in data:
        try:
            name = data[i]["nameDatabase"] + "_title"
            data[i]["nameZH"] = info[1][name]
            data[i]["nameFR"] = info[2][name]
        except:
            continue


def getPhaseOfTree():
    a = {} # a map from nameFile to tree id
    cnt = []
    for i in data:
        a[data[i]["nameFile"]] = i
        cnt.append(i)
    root = ".\\trees\\"
    info = {}
    phases = [[] for i in range(len(cnt) + 1)]
    for roots, dirs, files in os.walk(root):
        if roots != root:
            continue
        for file in files:
            curRoot = file.split("_phase_")[0]
            phase = file.split("_phase_")[1].split('.')[0]
            phases[a[curRoot]].append(phase)

    for i in cnt:
        info = {}
        dead = False
        christmas = False
        product = False
        ifForest = False
        xmas = []
        growth = []
        forest = []
        for phase in phases[i]:
            if phase == "dead":
                dead = True
                continue
            if phase == "product":
                product = True
                continue
            if phase.find("christmas") != -1:
                christmas = True
                xmas.append(int(phase.split("_christmas")[0][0]) - int('0'))
                continue
            if phase.find("forest") != -1:
                ifForest = True
                forest.append(int(phase.split("_forest")[0][0]) - int('0'))
                continue
            growth.append(int(phase[0]) - int('0'))
        info["hasDead"] = dead
        info["hasProduct"] = product
        info["hasChristmas"] = christmas
        info["hasForest"] = ifForest
        if christmas:
            if len(xmas) == 1:
                xmas = [xmas[0] for i in range(4)]
            info["christmas"] = xmas

        if ifForest:
            info["forest"] = forest
        elif christmas:
            if len(xmas) == 1:
                info["forest"] = [xmas[0] for i in range(4)]
            else:
                info["forest"] = xmas
        else:
            if growth[-1] == 7:
                info["forest"] = growth[-4::]
            else:
                info["forest"] = [growth[-1] for i in range(4)]

        info["growth"] = growth
        data[i]["phase"] = info


def exportToJson(data):
    f = open("treeType.json", "w", encoding = "utf-8")
    s = json.dumps(data, indent = 4, ensure_ascii = False)
    t = ""
    yes = False
    for i in s:
        if yes and (i == ' ' or i == '\n'):
            continue
        if yes and i == ',':
            t = t + ", "
            continue
        if i == ']':
            yes = False
        if i == '[':
            yes = True
        t = t + i
    f.write(t)
    f.close()

if __name__ == "__main__":
    data = {}

    getTreeName()
    getDescription()
    getPhaseOfTree()

    exportToJson(data)