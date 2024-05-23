import json
import xml.etree.ElementTree as ET
import os
import shutil


if __name__ == "__main__":
    forestRootDir = os.path.dirname(__file__) + "\\.."

    language = {"ZH": "values-zh-rCN", "EN": "values", "FR": "values-fr"}

    info = json.load(open(f"{forestRootDir}\\treeInfo.json", "r", encoding="utf-8"))
    data = {key: {} for key in info}
    for treeId in info:
        for lan in language:
            data[treeId][f"name{lan}"] = ""
        data[treeId]["nameXML"] = info[treeId]

    apkRootDir = forestRootDir
    apkFile = os.path.join(apkRootDir, "Forest 专注森林.apk")
    apkContentDir = f"{apkRootDir}\\testa"
    while os.path.exists(apkContentDir):
        apkContentDir += "(1)"
    os.system(f'echo y | apktool d "{apkFile}" -o "{apkContentDir}"')

    treeFileDir = os.path.join(apkContentDir, "res\\drawable-xxhdpi")
    treeStorageDir = f"{forestRootDir}\\trees"
    files = [x[2] for x in os.walk(treeFileDir)][0]
    treeImageList = []
    phaseInfo = {key: [] for key in info}
    treeFileToBeCopied = []
    for file in files:
        if not file.startswith("tree_type_") or file.endswith("launch.png"):
            continue
        curRoot = file.split("_phase_")[0].split("tree_type_")[1]
        phase = file.split("_phase_")[1].split(".")[0]
        if curRoot not in info:
            continue
        treeFileToBeCopied.append(
            (os.path.join(treeFileDir, file), os.path.join(treeStorageDir, file))
        )
        phaseInfo[curRoot].append(phase)

    # dynamicFileDir = os.path.join(apkContentDir, "res\\drawable")
    # dynamicStorageDir = f"{forestRootDir}\\treesDynamic"
    # files = [x[2] for x in os.walk(dynamicFileDir)][0]
    # isDynamic = {key: [False, False, False] for key in info}
    # switch = {'s': 0, 'a': 1, 'i': 2}
    # for file in files:
    #     if not file.startswith("frame_") or not file.endswith("webp"): continue
    #     treeId = file.split('_')[4]
    #     isDynamic[treeId][switch[file[6]]] = True
    #     treeFileToBeCopied.append((f"{dynamicFileDir}\\{file}", f"{dynamicStorageDir}\\{file}"))

    allPhaseInfo = {key: {} for key in info}
    for treeId in info:
        treePhaseInfo = {}
        dead, christmas = False, False
        growth, xmas = [], []
        if "dead" in phaseInfo[treeId]:
            dead = True
        for phase in phaseInfo[treeId]:
            if phase.find("christmas") != -1:
                xmas.append(int(phase[0]))
                christmas = True
            if phase.isdigit():
                growth.append(int(phase[0]))
        if len(xmas) == 1:
            xmas = [xmas[0] for i in range(4)]
        treePhaseInfo["hasDead"] = dead
        treePhaseInfo["hasChristmas"] = christmas
        # treePhaseInfo["hasStart"] = isDynamic[treeId][0]
        # treePhaseInfo["hasActive"] = isDynamic[treeId][1]
        # treePhaseInfo["hasIdle"] = isDynamic[treeId][2]
        treePhaseInfo["growth"] = growth
        if xmas:
            treePhaseInfo["xmas"] = xmas
        if len(growth) == 4:
            treePhaseInfo["forest"] = [growth[3] for i in range(4)]
        else:
            treePhaseInfo["forest"] = growth[-4::]
        allPhaseInfo[treeId] = treePhaseInfo

    for lan in language:
        xmlFile = f"{apkContentDir}\\res\\{language[lan]}\\strings.xml"
        root = ET.parse(xmlFile).getroot()
        for treeId in info:
            print(info[treeId])
            name = root.find(f"*[@name='{info[treeId]}_title']").text
            if name.find("'") != -1 or name.find("\n") != -1:
                name = name[1:-1]
            data[treeId][f"name{lan}"] = name
            element = root.find(f"*[@name='{info[treeId]}_description']")
            if element != None:
                description = element.text
                if description == None:
                    continue
                if description.find("'") != -1 or description.find("\n") != -1:
                    description = description[1:-1]
                data[treeId][f"description{lan}"] = description

    for treeId in info:
        data[treeId]["phase"] = allPhaseInfo[treeId]

    s, t = json.dumps(data, indent=4, ensure_ascii=False), ""
    yes = False
    for i in s:
        if yes and (i == " " or i == "\n"):
            continue
        if yes and i == ",":
            t = t + ", "
            continue
        if i == "]":
            yes = False
        if i == "[":
            yes = True
        t = t + i
    open(f"{forestRootDir}\\treeType.json", "w", encoding="utf-8").write(t)

    for src, dst in treeFileToBeCopied:
        shutil.move(src, dst)

    os.system(f"rmdir {apkContentDir} /S/Q")
