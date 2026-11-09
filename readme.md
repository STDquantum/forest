# Forest

双击根目录的 `打开网页.bat`，启动本地服务并打开首页（需要 Python 3）。主网页左上角可进入森林编辑器，浏览器自动保存收藏、布局和上次的选择。

双击根目录的 `一键更新.bat`，会自动从官网下载最新 APK，再更新树种、树图、地皮和网页数据到 `docs/`（需要 Python、Java 和 Apktool）。执行结束自动退出，无需按键；失败时停止后续步骤。本地更新不执行 Git 提交或推送。Python 查找方式与车模项目一致：优先使用 `PYTHON_HOME`，其次使用本机 `D:\conda\env3.10\python.exe`，最后使用 `py -3`。

已有 APK 时也可直接运行 `python main.py`。本机同步服务可用 `python scripts/serve_forest_web.py --open` 启动。

树种信息保存在 `docs/treeType.json`。

GitHub Pages 发布目录：`main` 分支的 `/docs`。

## 自动更新

`.github/workflows/update-forest.yml` 每周日北京时间 12:00（UTC 04:00）运行，也可在 Actions → Update Forest resources → Run workflow 手动运行。GitHub 的定时任务可能排队延迟，并非精确计时服务；工作流需要推送到默认分支才会定时生效。

流程先访问向上科技简体中文官网，从页面 JavaScript 中解析 Forest 安卓下载按钮使用的版本接口，再下载接口中 `apk_title` 指定的官方 APK。随后使用 JADX 和 Rive 渲染缺少的主题球体，再用 Java 21、Apktool 3.0.3 和 Python 3.12 执行 `python main.py`，有变化才将 `docs/` 提交回运行分支。APK 和解包目录不会提交；无需账号；工作流会安装 Pillow、JADX 和渲染所需依赖。分支保护若禁止机器人直接推送，需要调整仓库规则。

本地也可运行 `python scripts/download_forest_apk.py` 下载最新 APK，或加 `--resolve-only` 仅检查下载地址。Actions 通过 `APKTOOL_JAR` 指定 JAR，本地继续支持 PATH 中的 `apktool`（Windows 为 `apktool.bat`）。

网页发布沿用仓库现有的 `main` 分支 `/docs` 设置。首次自动更新后，应核对该提交是否产生成功的 Pages 部署记录；如果没有，再配置显式的 Pages Actions 部署流程。GitHub 文档描述了 `GITHUB_TOKEN` 提交不触发 Pages 构建的限制，但同账号的 `sparkmodel-monitor` 仓库已存在机器人提交后自动构建并部署成功的实际记录，不能据此断言本仓库一定不会自动发布。

## 首页图片资源

首页使用独立的球体 WebP 和各树种生长阶段 WebP。默认、圣诞及 02–08 球体使用已生成的新版静态图，APK 更新不会覆盖；已有的 09 及以后球体继续从 APK 更新；自动更新发现新主题时，先从 Rive 渲染缺少的球体。

## 首页资源与 Rive 参数

APK 是 ZIP 文件，首页资源位于 `assets/composeResources/com.seekrtech.stforestkit.resources/files/`：

| APK 内相对路径 | 内容 |
| --- | --- |
| `rive/focus_screen.riv` | 首页 Rive 场景，包含球体资源；生成球体时使用 `plant ball` 画板和 `State Machine 1` 状态机。 |
| `plant/theme_N.webp` | 主题图集，包含地面及装饰；当前 APK 中主题 0–10 的图集均为 4900×1840。 |
| `plant/tree_N.webp` | 树种图集；例如 `tree_97.webp` 为 1440×1440 的 3×3 图集，每格 480×480。 |

网站使用 `docs/assets/ball/` 中的完整球体图和 `docs/assets/trees/` 中各阶段独立的树图。首页将两者叠加，树图按生长阶段切换；森林编辑器的地面图块位于 `docs/assets/ground/`。

从 APK 反编译后，`com/seekrtech/stforestkit/` 下的主要代码位置和绑定关系如下：

| 相对路径 | 用途 |
| --- | --- |
| `landskin/presentation/LandSkinPaletteKt.java` | 主题对应的图集、场景参数和颜色；渲染脚本从这里提取参数。 |
| `landskin/domain/LandSkinScene.java` | 地面装饰、前景、云和景物的位置、缩放、旋转与透明度字段。 |
| `plant/domain/PlantBallArt.java` | 树图路径、最大生长阶段及运动类型。 |
| `app/focus/presentation/FocusRiveViewKt.java` 及其闭包 | 通过 `vmPlantBall/imgTheme` 绑定主题图，通过 `vmPlantBall/vmTreePlantBall/imgTree` 绑定树图，并设置阶段及主题颜色。 |

渲染球体时，场景参数写入 `numDeco*`、`numForeground*`、`numCloud1*`、`numCloud2*` 和 `numLandscape1/2/3*`；颜色写入 `clrThemeBg1/2/3`、`clrThemeFilter1/2/3` 等属性。导出时隐藏树图，树由首页单独叠加。

`focus_screen.riv` 中 `plant ball` 画板为 400×400，原点为中心；其直接嵌入的 `tree` 画板为 168×168，节点坐标为 x=0、y=-40，默认缩放为 1。树画板中的树图图集节点缩放为 0.35。首页树图的位置和尺寸根据这些静态值，并结合球图导出时的画布变换与网页 1.25 倍球图缩放计算。

输出画布为 936×936。为与现有球体图对齐，脚本将渲染球体中心从约 `(466.696, 443.867)` 调整至 `(467, 467.5)`，缩放系数为 `1.04514`。这些值是项目导出图片时的对齐参数；Rive 原始布局由画板决定。

## 从 APK 生成 Rive 球体图片

首页使用静态 WebP，Rive 只在生成图片时使用。脚本每次从指定 APK 读取 `focus_screen.riv` 和 `theme_N.webp`，用 JADX 反编译 `LandSkinPaletteKt`，提取各主题的场景参数和颜色，再将参数与主题图绑定到 Rive 的 `plant ball` 画板，隐藏树木并渲染透明图片。最后输出 936×936 的无损 WebP，并将球体尺寸和位置对齐现有图片。

需要 Python 3.9 以上及 Pillow（`python -m pip install Pillow`）、Java、Node.js/npm、Chrome 或 Edge，以及项目内的 `tools/jadx`（也可用 `--jadx` 指定）。脚本运行时会在临时目录通过 npm 下载 Rive Canvas 和 Playwright，不会把运行库放进网页。

```powershell
# 自动扫描 APK，只生成目录中尚不存在的球体图片
python scripts/render_ball_rive.py "Forest 专注森林.apk"

# 指定主题编号；已有图片会跳过
python scripts/render_ball_rive.py "Forest 专注森林.apk" --themes 0 1 2 10

# 直接替换首页图片
python scripts/render_ball_rive.py "Forest 专注森林.apk" --themes 9 10 --replace
```

如果浏览器不能以无头模式启动，可加 `--manual`，脚本会打开本机浏览器完成渲染；如果没自动打开，访问终端显示的本地地址即可。也可用 `--browser` 指定浏览器路径，用 `--output` 指定输出目录。编号 0、1 对应默认、圣诞，2 及以后对应 `groundNN`。

默认直接写入首页使用的文件名，已有文件会跳过；只有显式指定 `--themes` 和 `--replace` 才会覆盖已有文件。脚本不锁定 APK 版本；新 APK 会重新提取参数和资源。当前解析遵循现有 APK 的构造顺序、资源命名和 Rive 属性结构，若新版改变这些结构，需要调整脚本后再运行。日常 APK 更新仍会正常更新已有的 09 及以后主题图片；新主题先通过 Rive 生成球体。若要重新渲染已有主题，可运行上述 `--replace` 命令。
