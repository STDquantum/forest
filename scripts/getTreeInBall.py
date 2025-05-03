import json
import cv2
import os

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
    ball = cv2.resize(ball, dsize=(width, width))
    tree = cv2.imread(tree, cv2.IMREAD_UNCHANGED)
    tree = cv2.resize(tree, dsize=(int(width * 0.53), int(width * 0.53)))
    # display(ball)

    alphaTree = tree[:, :, 3] / 255.0
    alphaBall = 1 - alphaTree

    top = int((width - width * 0.53) // 3.5)
    bottom = int(top + width * 0.53)
    left = int((width - width * 0.53) // 2)
    right = int(width * 0.53) + left
    ball[top:bottom, left:right, :3] = (alphaTree[..., None] * tree[..., :3]) + (alphaBall[..., None] * ball[top:bottom, left:right, :3])
    
    # display(ball)
    return ball


def main():
    d = json.load(open(".\\treeType.json", "r", encoding = "utf-8"))
    root = os.path.dirname(__file__) + "\\.."
    
    treeMap = {}
    treeDir = os.path.join(root, "trees")
    treesFileNames = os.listdir(treeDir)
    for tree in treesFileNames:
        treeName = os.path.splitext(tree)[0]
        treeMap[treeName] = tree
        
    for b, tree in d.items():
        name = f"tree_type_{b}"

        for i in d[b]["phase"]["growth"]:
            treePhase = f"{name}_phase_{i}"
            tree = os.path.join(treeDir, treeMap[treePhase])
            treeDst = embedTree(tree, 960, "christmas")
            cv2.imwrite(os.path.join(root, f"growth\\ball\\{name}_{i}.png"), treeDst)

            # tree = "{}{}_{}.png".format(root, name, i)
            # treeDst = embedTree(tree, 480, "birthday")
            # cv2.imwrite(".\\growth\\ball\\{}_{}_hbd.png".format(name, i), treeDst)

        # if d[b]["phase"]["hasChristmas"] == True:
        #     l1 = d[b]["phase"]["growth"]
        #     l1 = list(set(l1))
        #     for i in l1:
        #         tree = "{}{}_{}_christmas.png".format(root, name, i)
        #         treeDst = embedTree(tree, 480, "christmas")
        #         cv2.imwrite(".\\growth\\ball\\{}_{}_christmas.png".format(name, i), treeDst)

        # if d[b]["phase"]["hasDead"] == True:
        #     tree = "{}{}_dead.png".format(root, name)
        #     treeDst = embedTree(tree, 480, "common")
        #     cv2.imwrite(".\\growth\\ball\\{}_dead.png".format(name), treeDst)


main()