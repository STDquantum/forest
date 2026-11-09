# Forest

双击根目录的 `打开网页.bat`，启动本地服务并打开首页（需要 Python 3）。主网页左上角可进入森林编辑器，浏览器自动保存收藏、布局和上次的选择。

双击根目录的 `一键更新.bat`，会自动从官网下载最新 APK，再更新树种、树图、地皮和网页数据到 `docs/`（需要 Python、Java 和 Apktool）。执行结束后自动退出。本地更新保存在工作区。Python 查找顺序为：优先使用 `PYTHON_HOME`，其次使用本机 `D:\conda\env3.10\python.exe`，最后使用 `py -3`。

已有 APK 时也可直接运行 `python main.py`。本机同步服务可用 `python scripts/serve_forest_web.py --open` 启动。

树种信息保存在 `docs/treeType.json`。

GitHub Pages 发布目录：`main` 分支的 `/docs`。

## 自动更新

`.github/workflows/update-forest.yml` 每周日北京时间 12:00（UTC 04:00）运行，也可在 Actions → Update Forest resources → Run workflow 手动运行。定时任务使用默认分支的工作流。

流程先访问向上科技简体中文官网，从页面 JavaScript 中解析 Forest 安卓下载按钮使用的版本接口，再下载接口中 `apk_title` 指定的官方 APK。随后使用 Rive 渲染缺少的主题球体，再用 Java 21、Apktool 3.0.3 和 Python 3.12 执行 `python main.py`，有变化才将 `docs/` 提交回运行分支。工作流安装 Pillow 和渲染依赖，并提交生成的网页资源。

本地也可运行 `python scripts/download_forest_apk.py` 下载最新 APK，或加 `--resolve-only` 仅检查下载地址。Actions 通过 `APKTOOL_JAR` 指定 JAR，本地使用 PATH 中的 `apktool`（Windows 为 `apktool.bat`）。


## 首页图片资源

首页使用独立的球体 WebP 和各树种生长阶段 WebP。自动更新保留已有球体图片，并通过 Rive 生成缺少的主题球体。

## 首页资源与 Rive 参数

APK 是 ZIP 文件，首页资源位于 `assets/composeResources/com.seekrtech.stforestkit.resources/files/`：

| APK 内相对路径 | 内容 |
| --- | --- |
| `rive/focus_screen.riv` | 首页 Rive 场景，包含球体资源；生成球体时使用 `plant ball` 画板和 `State Machine 1` 状态机。 |
| `plant/theme_N.webp` | 主题图集，包含地面及装饰；当前 APK 中主题 0–10 的图集均为 4900×1840。 |
| `plant/tree_N.webp` | 树种图集；例如 `tree_97.webp` 为 1440×1440 的 3×3 图集，每格 480×480。 |

网站使用 `docs/assets/ball/` 中的完整球体图和 `docs/assets/trees/` 中各阶段独立的树图。首页将两者叠加，树图按生长阶段切换；森林编辑器的地面图块位于 `docs/assets/ground/`。

球图使用主题图集渲染，树图由首页单独叠加。

`focus_screen.riv` 中 `plant ball` 画板为 400×400，原点为中心；其直接嵌入的 `tree` 画板为 168×168，节点坐标为 x=0、y=-40，默认缩放为 1。树画板中的树图图集节点缩放为 0.35。首页树图的位置和尺寸根据这些静态值，并结合球图导出时的画布变换与网页 1.25 倍球图缩放计算。

输出画布为 936×936。脚本将渲染球体中心从约 `(466.696, 443.867)` 调整至 `(467, 467.5)`，缩放系数为 `1.04514`，使球体与首页树图对齐。

## 从 APK 生成 Rive 球体图片

首页使用静态 WebP，Rive 只在生成图片时使用。脚本每次从指定 APK 读取 `focus_screen.riv` 和 `theme_N.webp`，将主题图绑定到 Rive 的 `plant ball` 画板，隐藏树木并渲染透明图片。最后输出 936×936 的无损 WebP，并将球体尺寸和位置对齐现有图片。

需要 Python 3.9 以上及 Pillow（`python -m pip install Pillow`）、Node.js/npm、Chrome 或 Edge。脚本运行时会在临时目录通过 npm 下载 Rive Canvas 和 Playwright。

```powershell
# 自动扫描 APK，只生成目录中尚不存在的球体图片
python scripts/render_ball_rive.py "Forest 专注森林.apk"

# 指定主题编号；已有图片会跳过
python scripts/render_ball_rive.py "Forest 专注森林.apk" --themes 0 1 2 10

# 直接替换首页图片
python scripts/render_ball_rive.py "Forest 专注森林.apk" --themes 9 10 --replace
```

可用 `--output` 指定输出目录。球图统一命名为 `groundNN_plant_ball.webp`；编号 00、01 分别对应默认和圣诞主题。

脚本按首页使用的文件名保存球图，默认跳过已有文件。使用 `--themes` 和 `--replace` 可重新渲染指定主题。
