import json
import sqlite3
import time
import matplotlib.pyplot as plt


def printf(path, things):
    with open(path, "w", encoding="utf-8") as f:
        f.write(things)


def init_from_database():
    conn = sqlite3.connect(rootDir + "databases\\Forest.db")
    c = conn.cursor()
    d = c.execute("SELECT id, start_time, end_time FROM Plants")
    conn.commit()
    e = []
    for i in d:
        e.append(list(i))
    e.sort(key=lambda x: x[1])

    for i, value in enumerate(e):
        d = c.execute(
            "SELECT tree_type FROM Trees WHERE plant_id = {}".format(value[0])
        )
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
        e[i] = e[i] + [
            start.tm_year,
            start.tm_mon,
            start.tm_mday,
            start.tm_hour,
            start.tm_min,
            start.tm_sec,
        ]
    # value[0 : 5] = [数据库内序号, 起始时间戳, 结束时间戳, id, phase]
    # value[5 : 11] = [年, 月, 日, 时, 分, 秒]
    return e


def treeType_not_planted(choice):
    d = json.load(
        open(rootDir + "treeType.json", "r", encoding="utf-8")
    )
    vis = [False for i in range(len(d))]

    if choice == 1:
        trees = init_from_json()
        for tree in trees:
            vis[tree["tree_type_gid"]] = True
    else:
        trees = init_from_database()
        for i, value in enumerate(trees):
            vis[value[3]] = True

    res = ""
    for i, value in enumerate(vis):
        if not value:
            res += "{}, ".format(d[str(i)]["nameZH"])
    if len(res) != 0:
        res = res[:-2]
    return res


def init_from_json():
    d = json.load(
        open(rootDir + "treeType.json", "r", encoding="utf-8")
    )
    user = json.load(
        open(rootDir + "databases\\user.json", "r", encoding="utf-8")
    )
    trees = json.load(
        open(rootDir + "databases\\plant.json", "r", encoding="utf-8")
    )
    rooms = json.load(
        open(rootDir + "databases\\rooms.json", "r", encoding="utf-8")
    )

    room = {}
    for i in rooms:
        room[i["id"]] = i

    for i, tree in enumerate(trees):
        s = (
            time.mktime(time.strptime(tree["start_time"][:-5], "%Y-%m-%dT%H:%M:%S"))
            + 8 * 3600
        )
        t = time.localtime(s)
        trees[i]["startTimeStamp"] = s
        trees[i]["timeDS"] = t
        end = (
            time.mktime(time.strptime(tree["end_time"][:-5], "%Y-%m-%dT%H:%M:%S"))
            + 8 * 3600
        )
        trees[i]["duration"] = int(round((end - s) / 60))
        trees[i]["nameZH"] = d[str(tree["tree_type_gid"])]["nameZH"]
        trees[i]["nameEN"] = d[str(tree["tree_type_gid"])]["nameEN"]
        if tree["room_id"] != None:
            trees[i]["room"] = room[tree["room_id"]]
    trees.sort(key=lambda x: x["startTimeStamp"])
    return trees


def trees_planted():
    trees = init_from_json()
    res = ""
    cnt = 0
    for i, tree in enumerate(trees):
        if tree["deleted"] == True:
            continue
        cnt += 1
        duration = ""
        if tree["duration"] < 60:
            duration = "{}min".format(tree["duration"])
        elif tree["duration"] % 60 == 0:
            duration = "{}h".format(tree["duration"] // 60)
        else:
            duration = "{}h{}min".format(tree["duration"] // 60, tree["duration"] % 60)
        res = (
            "{:3}. {:<{}} {}   {:<9} {} {}\n".format(
                cnt,
                tree["nameZH"],
                16 - len(tree["nameZH"].encode("GBK")) + len(tree["nameZH"]),
                time.strftime("%Y-%m-%d %H:%M:%S", tree["timeDS"]),
                duration,
                ""
                if tree["room_id"] == None
                else "{}人合种".format(tree["room"]["participants_count"]),
                tree["note"],
            )
            + res
        )

    return res


if __name__ == "__main__":
    from os.path import dirname
    rootDir = dirname(__file__) + "\\..\\"
    printf(rootDir + "plants.txt", trees_planted())
