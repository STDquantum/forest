import json
import cv2

def display(img):
    cv2.imshow("result", img)
    cv2.waitKey(0)

def embedTree(tree, width, theme):
    ball = ".\\background\\plant_ball"
    if theme == "common":
        ball = ball + ".png"
    elif theme == "birthday":
        ball = ball + "_hbd.png"
    elif theme == "christmas":
        ball = ball + "_christmas.png"

    ball = cv2.imread(ball, cv2.IMREAD_UNCHANGED)
    ball = cv2.resize(ball, dsize = (width, width))
    tree = cv2.imread(tree, cv2.IMREAD_UNCHANGED)
    tree = cv2.resize(tree, dsize = (int(width * 0.53), int(width * 0.53)))

    alphaTree = tree[:, :, 3] / 255.0
    alphaBall = 1 - alphaTree

    top = int((width - width * 0.53) // 3.5)
    bottom = int(top + width * 0.53)
    left = int((width - width * 0.53) // 2)
    right = int(width * 0.53) + left
    for c in range(3):
        ball[top : bottom, left : right, c] = (alphaBall * ball[top : bottom, left : right, c]) + (alphaTree * tree[:, :, c])
    
    # display(ball)
    return ball


if __name__ == "__main__":
    d = json.load(open(".\\treeType.json", "r", encoding = "utf-8"))
    now = 0
    while now >= 0:
        b = str(now)
        now = now + 1
        try:
            name = d[b]["nameFile"]
        except:
            break
        nameEN = d[b]["nameEN"]

        if d[b]["nameZH"] != '圣诞树':
            continue

        root = ".\\trees\\{}\\".format(name)
        for i in d[b]["phase"]["growth"]:
            tree = "{}{}_{}.png".format(root, name, i)
            treeDst = embedTree(tree, 480, "christmas")
            cv2.imwrite(".\\growth\\ball\\{}_{}.png".format(name, i), treeDst)

            # tree = "{}{}_{}.png".format(root, name, i)
            # treeDst = embedTree(tree, 480, "birthday")
            # cv2.imwrite(".\\growth\\ball\\{}_{}_hbd.png".format(name, i), treeDst)

        if d[b]["phase"]["hasChristmas"] == True:
            l1 = d[b]["phase"]["growth"]
            l1 = list(set(l1))
            for i in l1:
                tree = "{}{}_{}_christmas.png".format(root, name, i)
                treeDst = embedTree(tree, 480, "christmas")
                cv2.imwrite(".\\growth\\ball\\{}_{}_christmas.png".format(name, i), treeDst)

        if d[b]["phase"]["hasDead"] == True:
            tree = "{}{}_dead.png".format(root, name)
            treeDst = embedTree(tree, 480, "common")
            cv2.imwrite(".\\growth\\ball\\{}_dead.png".format(name), treeDst)
