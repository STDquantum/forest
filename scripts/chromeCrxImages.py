import json
import re
import os

def move(src, dst):
    if os.path.exists(dst):
        os.system('xcopy "{}" "{}" /Y/Q'.format(src, dst))
    else:
        os.system('echo f | xcopy "{}" "{}" /Q'.format(src, dst))

if __name__ == "__main__":
    default, christmas, birthday, tinytan = 0, 1, 2, 3
    theme = christmas

    root = "D:\\phpstudy\\azhe\\forest\\"
    root1 = "C:\\Users\\HUAWEI\\AppData\\Local\\Twinkstar\\User Data\\Default\\Extensions\\kjacjjdnoddnpbbcjilcajfhhbdhkpgk\\5.2.1_0\\"
    data = json.load(open(root + "treeType.json", "r", encoding = "utf-8"))
    treeCnt = len(data)
    treeJson = ""

    base = root + "trees\\"
    base1 = root1 + "images\\plants\\"
    for i in data:
        gid = int(i)
        print(gid)
        phases = data[i]["phase"]["growth"]
        hasChristmas = data[i]["phase"]["hasChristmas"]
        if hasChristmas:
            phasesXmas = data[i]["phase"]["xmas"]
        name = f"tree_type_{i}"
        for phase in phases:
            if theme == christmas and hasChristmas and phase in phasesXmas:
                src = base + name + "_phase_{}_christmas.png".format(phase)
            else:
                src = base + name + "_phase_{}.png".format(phase)
            dst = base1 + i + "\\" + str(phase) + ".png"
            move(src, dst)
        if data[i]["phase"]["hasDead"]:
            src = base + name + "_phase_dead.png"
            dst = base1 + i + "\\dead.png"
            move(src, dst)
        treeJson += "{id:" + i + ',phaseType:"'
        treeJson += "Seven" if len(phases) == 7 else "Four"
        treeJson += '",name:"' + data[i]["nameEN"] + '",images:{'
        for p in phases:
            treeJson += '"{p}":"./images/plants/{i}/{p}.png"'.format(p = p, i = gid)
            if p != phases[-1] or data[i]["phase"]["hasDead"]: 
                treeJson += ","
        if data[i]["phase"]["hasDead"]:
            treeJson += 'dead:"./images/plants/{}/dead.png"'.format(gid)
        treeJson += "}}"
        if gid != treeCnt - 1:
            treeJson += ","

    for file in ["background.js", "options.js"]:
        treeStr = open(root1 + file, "r", encoding = "utf-8").read()
        s = re.findall(r"(?<=\[)\{.*?\}\}(?=\])", treeStr)
        treeStr = treeStr.replace(s[0], treeJson)
        open(root1 + file, "w", encoding = "utf-8").write(treeStr)

    print("plant ball")
    src = root + "background\\plant_ball.png"
    if theme == christmas:
        src = root + "background\\plant_ball_christmas.png"
    elif theme == birthday:
        src = root + "background\\plant_ball_hbd.png"
    elif theme == tinytan:
        src = root + "background\\tinytan_plant_ball.png" 
    ballList = ["plant-ball-3IVJV4LF.png", "plant-ball-IEGHSBP6.png"]
    for ball in ballList:
        move(src, root1 + ball)

    print("earth")
    src = root + "background\\ground_piece.png"
    if theme == christmas:
        src = root + "background\\ground_piece_xmas.png"
    elif theme == tinytan:
        src = root + "background\\tinytan_ground_piece.png"
    dst = root1 + "ground-piece-LLMV3YMI.png"
    move(src, dst)

    src = root + "background\\ground_left_side.png"
    if theme == christmas:
        src = root + "background\\left_xmas.png"
    elif theme == tinytan:
        src = root + "background\\tinytan_ground_left_side.png"
    dst = root1 + "ground-left-YH3VQTLM.png"
    move(src, dst)

    src = root + "background\\ground_right_side.png"
    if theme == christmas:
        src = root + "background\\right_xmas.png"
    elif theme == tinytan:
        src = root + "background\\tinytan_ground_right_side.png"
    dst = root1 + "ground-right-63ETKNDR.png"
    move(src, dst)