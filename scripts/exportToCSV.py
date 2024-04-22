import sqlite3
import time
import json

def monthAndWeekdayNames():
    dicMonth = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec"
    }
    dicWeekday = {
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thu",
        5: "Fri",
        6: "Sat",
        7: "Sun"
    }
    return dicMonth, dicWeekday

if __name__ == "__main__":
    f = open(".\\databases\\Plants of 405720329@qq.com (STDquantum).csv", "w", encoding = "utf-8")
    f.write('"Start Time","End Time","Tag","Note","Tree Type","Is Success"\n')

    conn = sqlite3.connect(".\\databases\\Forest.db")
    c = conn.cursor()
    d = c.execute("SELECT id, start_time, end_time, is_success, tag_id, note FROM Plants")
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
    
    dicMonth, dicWeekday = monthAndWeekdayNames()
    for j, i in enumerate(e):
        start, end = map(time.localtime, (i[1] / 1000, i[2] / 1000))
        e[j][1] = '"{} {} {:02} {:02}:{:02}:{:02} GMT+08:00 {}"'.format(dicWeekday[start.tm_wday + 1], dicMonth[start.tm_mon], start.tm_mday, start.tm_hour, start.tm_min, start.tm_sec, start.tm_year)
        e[j][2] = '"{} {} {:02} {:02}:{:02}:{:02} GMT+08:00 {}"'.format(dicWeekday[end.tm_wday + 1], dicMonth[end.tm_mon], end.tm_mday, end.tm_hour, end.tm_min, end.tm_sec, end.tm_year)


    d = c.execute("SELECT tag_id, tag FROM PlantTags")
    conn.commit()
    a = {}
    for tagId, tag in d:
        a[tagId] = tag
    for j, i in enumerate(e):
        if e[j][3] == 1: 
            e[j][3] = '"True"'
        else: 
            e[j][3] = '"False"'

        try:
            e[j][4] = '"{}"'.format(a[e[j][4]])
        except:
            e[j][4] = '"未设定"'
        e[j][5] = '"{}"'.format(e[j][5])

    
    d = json.load(open(".\\treeType.json", "r", encoding = "utf-8"))
    for j, i in enumerate(e):
        e[j][6] = '"{}"'.format(d["{}".format(e[j][6])]["nameZH"])
        e[j] = i[1:]

    for i in e:
        f.write("{},{},{},{},{},{}\n".format(i[0], i[1], i[3], i[4], i[5], i[2]))