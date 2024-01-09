import cv2
import numpy
import sqlite3
import os
import math
import json
import time
import random

def numpyArray_of_Tree():
    numpy.set_printoptions(threshold = numpy.inf)
    tree = cv2.imread(".\\trees\\pear_tree_house\\pear_tree_house_3.png", cv2.IMREAD_UNCHANGED)
    with open("1.txt", "w") as f:
        f.write(str(tree))

def move_some_same_growth():
    d = json.load(open("treeType.json", "r", encoding = "utf-8"))
    a = [".\\trees\\cedar\\cedar_{}.png".format(i) for i in range(3)]
    print(a)
    for key in d:
        name = d[key]["nameFile"]
        firstForest = d[key]["phase"]["forest"][0]
        place = d[key]["phase"]["growth"].index(firstForest)
        if place <= 2:
            print(d[key]["nameZH"], d[key]["phase"]["growth"])
            for i in range(1, 4 - place):
                os.system("xcopy /y {0} .\\trees\\{1}\\{1}_{2}.png".format(a[i - 1], name, i))

def timeStamp_to_Time(timeStamp):
    # print("{}-{0:2}-{}"time.localtime(timeStamp / 1000))
    a = 1

def which_tree_hasnt_christmas():
    data = json.load(open("treeType.json", "r", encoding = "utf-8"))
    for tree in data.values():
        if tree["phase"]["hasChristmas"] == False:
            print(tree["nameZH"])

def get_new_treeInfo():
    d = json.load(open("treeType.json", "r", encoding = "utf-8"))
    d1 = {}
    for key in d:
        d1[key] = {}
        d1[key]["nameEN"] = d[key]["nameEN"]
        d1[key]["nameFile"] = d[key]["nameFile"]
        d1[key]["nameDatabase"] = d[key]["nameDatabase"]
    json.dump(d1, open("treeInfo.json", "w", encoding = "utf-8"), indent = 4)

def plant_personalize():
    s = "["
    start, end = 0, 86 # [start, end]
    for i in range(start, end + 1):
        s += "[1,{},6,7]".format(i) + ("," if i != end else "")
    s += "]"
    with open("1.json", "w") as f:
        f.write(s)

def init_from_database():
    conn = sqlite3.connect(".\\databases\\Forest.db")
    c = conn.cursor()
    d = c.execute("SELECT id, start_time, end_time FROM Plants")
    conn.commit()
    e = []
    for i in d:
        e.append(list(i))
    e.sort(key = lambda x : x[1])

    for i, value in enumerate(e):
        d = c.execute("SELECT tree_type FROM Trees WHERE plant_id = {}".format(value[0]))
        conn.commit()
        for j in d:
            value.append(j[0])
            break
        d = c.execute("SELECT phase FROM Trees WHERE plant_id = {}".format(value[0]))
        conn.commit()
        tmp = []
        for j in d:
            tmp.append(j[0])
        value.append(tmp)
        start = time.localtime(value[1] / 1000)
        e[i] = e[i] + [start.tm_year, start.tm_mon, start.tm_mday, start.tm_hour, start.tm_min, start.tm_sec]

    trees = []
    total = 0
    # value[0 : 5] = [数据库内id, 起始时间戳, 结束时间戳, gid, phase]
    # value[5 : 11] = [年, 月, 日, 时, 分, 秒]
    for i, value in enumerate(e):
        if not (True): # Decide what not to put in the image
            continue
        total = total + len(value[4])
        trees.append(value[3 : 5])
    
    return trees, total

def display(img, seconds = 0):
    cv2.imshow("result", img)
    cv2.waitKey(seconds * 1000)

def shadow():
    # shadows
    # shadowHeight = int(shadowWidth * 0.6)
    # shadowWidth = int(pieceWidth * 0.5)
    # shadowXOffset = int(pieceWidth * 0.25)
    # shadowYOffset = int(pieceHeight * 0.25)
    # shadow = cv2.imread(".\\background\\tree_shadow.png", cv2.IMREAD_UNCHANGED)
    # shadow = cv2.resize(shadow, dsize = (shadowWidth, shadowHeight))
    # now = 0
    # for pos in piecePosList:
    #     while now in emptyPosList:
    #         now += 1
    #     if now >= posCnt: break
    #     posX = piecePosList[i].x + shadowXOffset
    #     posY = piecePosList[i].y + shadowYOffset
    #     combine(shadow, Pos(posX, posY))
    #     now += 1
    a = 1

if __name__ == "__main__":
    a = 1
    plant_personalize()
    