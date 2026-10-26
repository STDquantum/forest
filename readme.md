# Forest

双击根目录的 `打开网页.bat`，或直接打开 `docs/index.html`。主网页左上角可进入森林编辑器，浏览器自动保存收藏、布局和上次的选择。

更新根目录的 APK 后运行 `python main.py`（需要 Java 和 Apktool），树图、地皮和网页数据会直接更新到 `docs/`。本机同步服务可用 `python scripts/serve_forest_web.py --open` 启动。

树种信息保存在 `docs/treeType.json`。

GitHub Pages 发布目录：`main` 分支的 `/docs`。

## 自动更新

`.github/workflows/update-forest.yml` 每周日北京时间 12:00（UTC 04:00）运行，也可在 Actions → Update Forest resources → Run workflow 手动运行。GitHub 的定时任务可能排队延迟，并非精确计时服务；工作流需要推送到默认分支才会定时生效。

流程先访问向上科技简体中文官网，从页面 JavaScript 中解析 Forest 安卓下载按钮使用的版本接口，再下载接口中 `apk_title` 指定的官方 APK。随后用 Java 21、Apktool 3.0.3 和 Python 3.12 执行 `python main.py`，有变化才将 `docs/` 提交回运行分支。APK 和解包目录不会提交；无需账号或额外 Python 依赖。分支保护若禁止机器人直接推送，需要调整仓库规则。

本地也可运行 `python scripts/download_forest_apk.py` 下载最新 APK，或加 `--resolve-only` 仅检查下载地址。Actions 通过 `APKTOOL_JAR` 指定 JAR，本地继续支持 PATH 中的 `apktool`（Windows 为 `apktool.bat`）。

注意：`GITHUB_TOKEN` 自动推送的提交不会触发基于分支的 GitHub Pages 构建；此工作流负责更新仓库数据。如果需要自动发布网页，需要另外配置 Pages 的 Actions 部署流程。
