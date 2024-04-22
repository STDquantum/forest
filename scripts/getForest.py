import cv2
import numpy
from json import load
import random
from math import ceil, sqrt
import time

default, christmas, tinytan = 0, 1, 2

class TreeProps:
    year: int
    month: int
    day: int
    weekday: int # 1~7, from Monday
    phases: list
    gid: int
    startTime: int
    endTime: int
    deleted: bool
    roomId = None
    duration: float # By minutes
    room: dict
    nameZH: str
    nameEN: str

    def __init__(s):
        s.year = s.month = s.day = s.weekday = 0
        s.phases = []
        s.gid = s.startTime = s.endTime = s.duration = 0
        s.roomId = None
        s.deleted = False
        s.room = {}
        s.nameEN = s.nameZH = ""
    
    def setTime(self, startTimeStamp, endTimeStamp):
        timeDS = time.localtime(startTimeStamp)
        self.startTime, self.endTime = startTimeStamp, endTimeStamp
        self.year, self.month, self.day = timeDS.tm_year, timeDS.tm_mon, timeDS.tm_mday
        self.weekday = 7 if timeDS.tm_wday == 0 else timeDS.tm_wday

class Pos:
    x: int
    y: int
    def __init__(self, x, y):
        self.x, self.y = x, y

def selected(tree: TreeProps):
    return True
    return tree.year == 2023
    return tree.year == 2022 and ((tree.month == 1 and tree.day >= 20) or (tree.month == 2))

def init_from_json():
    d = load(open(rootDir + "treeType.json", "r", encoding = "utf-8"))
    trees = load(open(rootDir + "databases\\plant.json", "r", encoding = "utf-8"))
    rooms = load(open(rootDir + "databases\\rooms.json", "r", encoding = "utf-8"))
    room = {}
    for i in rooms:
        room[i["id"]] = i

    newTrees = [TreeProps() for i in range(len(trees))]
    for i, tree in enumerate(trees):
        s = time.mktime(time.strptime(tree["start_time"][:-5], "%Y-%m-%dT%H:%M:%S")) + 8 * 3600
        end = time.mktime(time.strptime(tree["end_time"][:-5], "%Y-%m-%dT%H:%M:%S")) + 8 * 3600
        newTrees[i].setTime(s, end)
        newTrees[i].duration = int(round((end - s) / 60))
        newTrees[i].gid = tree["tree_type_gid"]
        newTrees[i].nameZH = d[str(newTrees[i].gid)]["nameZH"]
        newTrees[i].nameEN = d[str(newTrees[i].gid)]["nameEN"]
        newTrees[i].deleted = tree["deleted"]
        for phase in tree["trees"]:
            newTrees[i].phases.append(phase["phase"] - 1)
        if tree["room_id"] != None:
            newTrees[i].roomId = tree["room_id"]
            newTrees[i].room = room[tree["room_id"]]
    newTrees.sort(key = lambda x : x.startTime)

    res = []
    total = 0
    for tree in newTrees:
        if tree.deleted == True:
            continue
        if not selected(tree): # Decide what to put in the image
            continue
        total += len(tree.phases)
        res.append(list((tree.gid, tree.phases)))
    
    return res, total

def personnalization():
    res = []
    total = 0
    trees = load(open(rootDir + "test.json", "r"))
    for tree in trees:
        info = list((tree[1], tree[2:]))
        for i in range(tree[0]):
            res.append(info)
        total += (len(tree) - 2) * tree[0]
    return res, total

def combine(img, pos: Pos):
    w, h = img.shape[1], img.shape[0]
    Y1, Y2, X1, X2 = map(int, (pos.y, pos.y + h, pos.x, pos.x + w))
    srcAlpha = img[:, :, 3] / 255.0
    dstAlpha = 1 - srcAlpha
    for i in range(3):
        bg[Y1 : Y2, X1 : X2, i] = dstAlpha * bg[Y1 : Y2, X1 : X2, i] + srcAlpha * img[:, :, i]

def forest(trees, edgeLen, theme = default, isRandom = False):
    piecePosList = []
    leftGroundPosList = []
    rightGroundPosList = []
    pieceHeight = 220
    pieceWidth = int(pieceHeight * 2)
    edgeWidth = int(pieceWidth / 2) + 1
    edgeHeight = int(pieceHeight * 1.5)
    earthHeight = int(pieceHeight * (edgeLen + 1))
    canvasHeight = int(earthHeight + pieceHeight * 1.5)
    canvasWidth = int(pieceWidth * edgeLen + pieceHeight * 0.2)
    treeWidth = int(pieceWidth * 0.8)
    treeHeight = int(treeWidth)
    treeXOffset = int(pieceWidth * 0.1)
    treeYOffset = int(pieceHeight * 0.75 - treeHeight)

    initialPos = Pos(
        x = canvasWidth // 2 - pieceWidth // 2,
        y = canvasHeight - earthHeight
    )

    for i in range(edgeLen):
        iPosX = initialPos.x + (pieceWidth / 2) * i
        iPosY = initialPos.y + (pieceHeight / 2) * i
        for j in range(edgeLen):
            posX = iPosX - j * (pieceWidth / 2)
            posY = iPosY + j * (pieceHeight / 2)
            piecePosList.append(Pos(posX, posY));

    if isRandom:
        random.shuffle(piecePosList)

    initialGroundLPosX = initialPos.x - (edgeLen - 1) * (pieceWidth / 2)
    initialGroundLPoxY = initialPos.y + edgeLen * (pieceHeight / 2)
    for i in range(edgeLen):
        leftGroundPosList.append(Pos(
            initialGroundLPosX + i * (pieceWidth / 2),
            initialGroundLPoxY + i * (pieceHeight / 2)
        ))

    initialGroundRPosX = initialPos.x + edgeLen * (pieceWidth / 2)
    initialGroundRPoxY = initialPos.y + edgeLen * (pieceHeight / 2)
    for i in range(edgeLen):
        rightGroundPosList.append(Pos(
            initialGroundRPosX - i * (pieceWidth / 2),
            initialGroundRPoxY + i * (pieceHeight / 2)
        ))

    global bg
    bg = numpy.zeros((canvasHeight, canvasWidth, 4), dtype = numpy.uint8)

    # groundPieces
    groundPng = {
        0: "ground_piece.png",
        1: "ground_piece_xmas.png",
        2: "tinytan_ground_piece.png"
    }
    piece = cv2.imread(rootDir + f"background\\{groundPng[theme]}", cv2.IMREAD_UNCHANGED)
    piece = cv2.resize(piece, dsize = (pieceWidth, pieceHeight))
    for pos in piecePosList:
        combine(piece, pos)

    # groundL
    groundLPng = {
        0: "ground_left_side.png",
        1: "left_xmas.png",
        2: "tinytan_ground_left_side.png"
    }
    groundL = cv2.imread(rootDir + f"background\\{groundLPng[theme]}", cv2.IMREAD_UNCHANGED)
    groundL = cv2.resize(groundL, dsize = (edgeWidth, edgeHeight))
    for pos in leftGroundPosList:
        combine(groundL, pos)

    # groundR
    groundRPng = {
        0: "ground_right_side.png",
        1: "right_xmas.png",
        2: "tinytan_ground_right_side.png"
    }
    groundR = cv2.imread(rootDir + f"background\\{groundRPng[theme]}", cv2.IMREAD_UNCHANGED)
    groundR = cv2.resize(groundR, dsize = (edgeWidth, edgeHeight))
    for pos in rightGroundPosList:
        combine(groundR, pos)

    # emptyPositions
    treeData = load(open(rootDir + "treeType.json", "r", encoding = "utf-8"))
    fileList = []
    for tree, phases in trees:
        gid = str(tree)
        nameFile = f"tree_type_{gid}"
        base = rootDir + f"trees\\{nameFile}_phase_"
        for phase in phases:
            if phase == 7:
                if treeData[gid]["phase"]["hasDead"] == True:
                    fileList.append(base + "dead.png")
            elif phase in [3, 4, 5, 6]:
                now = treeData[gid]["phase"]["forest"][phase - 3]
                if theme == christmas and treeData[gid]["phase"]["hasChristmas"] == True:
                    fileList.append(base + f"{now}_christmas.png")
                else:
                    fileList.append(base + f"{now}.png")
    posCnt = edgeLen * edgeLen
    emptyPosList = numpy.random.randint(posCnt, size = posCnt - len(fileList))

    # trees
    treeImg = {}
    now = 0
    for file in fileList:
        while now in emptyPosList:
            now += 1
        if file in treeImg:
            tree = treeImg[file]
        else:
            tree = cv2.imread(file, cv2.IMREAD_UNCHANGED)
            tree = cv2.resize(tree, dsize = (treeWidth, treeHeight))
            treeImg[file] = tree
        posX = piecePosList[now].x + treeXOffset
        posY = piecePosList[now].y + treeYOffset
        combine(tree, Pos(posX, posY))
        now += 1
                        
    bg[:, :, 3] = 255
    cv2.imwrite(rootDir + "test.png", bg)

if __name__ == "__main__":
    from os.path import dirname
    rootDir = dirname(__file__) + "\\..\\"
    s = time.time()
    # trees, total = personnalization()
    trees, total = init_from_json()
    forest(trees, ceil(sqrt(total)), theme = christmas, isRandom = True)
    e = time.time()
    print("%.3fs" % float(e - s))