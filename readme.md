## 使用方法

需要在 treeInfo.json 注册一下树种在 XML 里的名字，到后面都标准化了，直接写 tree_type_102 之类的就行。

把 apk 扔到项目根目录，名字复制到 scripts/treeNamesRebuild.py 28行，直接跑。

## Some tips in case forget

```python
png_Img = cv2.imread("Where it is.png", cv2.IMREAD_UNCHANGED)
dst = cv2.resize(src, dsize = (x, y))
y, x = png.shape[0], png.shape[1]

Transparent_Png = numpy.zeros((y, x, 4), dtype = numpy.uint8)

def seeInto(img):
    numpy.set_printoptions(threshold = numpy.inf)
    with open("1.txt", "w") as f:
        f.write(str(img))

def combine_Two_Img(A, B):
    # yB2 - yB1 = yA2 - yA1, xB2 - xB1 = xA2 - xA1
    # If B itself is to be combined, you can use B[:, :, dimention].
    srcAlpha = B[yB1 : yB2, xB1 : xB2, 3] / 255.0
    dstAlpha = 1 - srcAlpha
    for c in range(3):
        A[yA1 : yA2, xA1 : xA2, c] = dstAlpha * A[yA1 : yA2, xA1 : xA2, c] + srcAlpha * B[yB1 : yB2, xB1 : xB2, c]

# load data from json file
data = json.load(open("file.json", "r", encoding = "utf-8"))
# save data to json file
json.dump(data, open("file.json", "w", encoding = "utf-8"), indent = 4, ensure_ascii = False)

# struct_time has attributes tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec...
timeStamp_to_formatTime = time.strftime("%Y-%m-%d %H:%M:%S", timeStamp)
formatTime_to_timeStamp = time.mktime(time.strptime(timeStr, "%Y-%m-%d %H:%M:%S"))
```