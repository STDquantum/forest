# Forest

双击根目录的 `打开网页.bat`，或直接打开 `docs/index.html`。主网页左上角可进入森林编辑器，浏览器自动保存收藏、布局和上次的选择。

双击根目录的 `一键更新.bat`，会自动从官网下载最新 APK，再更新树种、树图、地皮和网页数据到 `docs/`（需要 Python、Java 和 Apktool）。执行结束自动退出，无需按键；失败时停止后续步骤。本地更新不执行 Git 提交或推送。Python 查找方式与车模项目一致：优先使用 `PYTHON_HOME`，其次使用本机 `D:\conda\env3.10\python.exe`，最后使用 `py -3`。

已有 APK 时也可直接运行 `python main.py`。本机同步服务可用 `python scripts/serve_forest_web.py --open` 启动。

树种信息保存在 `docs/treeType.json`。

GitHub Pages 发布目录：`main` 分支的 `/docs`。

## 自动更新

`.github/workflows/update-forest.yml` 每周日北京时间 12:00（UTC 04:00）运行，也可在 Actions → Update Forest resources → Run workflow 手动运行。GitHub 的定时任务可能排队延迟，并非精确计时服务；工作流需要推送到默认分支才会定时生效。

流程先访问向上科技简体中文官网，从页面 JavaScript 中解析 Forest 安卓下载按钮使用的版本接口，再下载接口中 `apk_title` 指定的官方 APK。随后用 Java 21、Apktool 3.0.3 和 Python 3.12 执行 `python main.py`，有变化才将 `docs/` 提交回运行分支。APK 和解包目录不会提交；无需账号或额外 Python 依赖。分支保护若禁止机器人直接推送，需要调整仓库规则。

本地也可运行 `python scripts/download_forest_apk.py` 下载最新 APK，或加 `--resolve-only` 仅检查下载地址。Actions 通过 `APKTOOL_JAR` 指定 JAR，本地继续支持 PATH 中的 `apktool`（Windows 为 `apktool.bat`）。

网页发布沿用仓库现有的 `main` 分支 `/docs` 设置。首次自动更新后，应核对该提交是否产生成功的 Pages 部署记录；如果没有，再配置显式的 Pages Actions 部署流程。GitHub 文档描述了 `GITHUB_TOKEN` 提交不触发 Pages 构建的限制，但同账号的 `sparkmodel-monitor` 仓库已存在机器人提交后自动构建并部署成功的实际记录，不能据此断言本仓库一定不会自动发布。
