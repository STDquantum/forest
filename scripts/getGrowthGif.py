import json
import PIL.Image as Image
import numpy
import cv2
import os


def display(img, seconds=1):
    cv2.imshow("result", img)
    cv2.waitKey(seconds * 1000)


def convert(path, dstX, dstY):
    png = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    x = png.shape[1]
    y = png.shape[0]
    bg = numpy.zeros((y, x), dtype=numpy.uint8)
    bg = cv2.cvtColor(bg, cv2.COLOR_GRAY2BGR)

    alpha_png = png[:, :, 3] / 255.0
    alpha_bg = 1 - alpha_png

    for c in range(3):
        bg[:, :, c] = (alpha_bg * bg[:, :, c]) + (alpha_png * png[:, :, c])

    bg = cv2.resize(bg, dsize=(dstY, dstX))
    return bg


if __name__ == "__main__":
    root = os.path.dirname(__file__) + "\\.."
    d = json.load(open(os.path.join(root, "treeType.json"), "r", encoding="utf-8"))
    for b in d:
        name = f"tree_type_{b}"
        nameEN = d[b]["nameEN"]
        growth = []
        treeRootPath = os.path.join(root, f"trees\\{name}")
        for i in d[b]["phase"]["growth"]:
            growth.append(f"{treeRootPath}_phase_{i}.png")
        if d[b]["phase"]["hasChristmas"] == True:
            l1 = d[b]["phase"]["xmas"]
            l1 = list(set(l1))
            for i in l1:
                growth.append(f"{treeRootPath}_phase_{i}_christmas.png")
        growth.append(f"{treeRootPath}_phase_dead.png")

        x = 0x3F3F3F3F
        y = 0x3F3F3F3F
        for path in growth:
            try:
                png = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                x = min(x, png.shape[1])
                y = min(y, png.shape[0])
            except:
                continue

        frame = []
        for path in growth:
            try:
                b, g, r = cv2.split(convert(path, x, y))
                img = cv2.merge([r, g, b])
                pil_img = Image.fromarray(img)
                frame.append(pil_img)
            except:
                continue
        gif_name = os.path.join(root, f"growth\\GIF\\{nameEN}.gif")
        frame[0].save(gif_name, format="GIF", save_all=True, append_images=frame[1:], duration=1000, loop=0)
        print(f"{nameEN} completed!")
