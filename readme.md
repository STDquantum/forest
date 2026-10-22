# Forest

双击根目录的 `打开网页.bat`，或直接打开 `docs/index.html`。主网页左上角可进入森林编辑器，浏览器自动保存收藏、布局和上次的选择。

更新根目录的 APK 后运行 `python main.py`（需要 Java 和 Apktool），树图、地皮和网页数据会直接更新到 `docs/`。本机同步服务可用 `python scripts/serve_forest_web.py --open` 启动。

树种信息保存在 `docs/treeType.json`。

GitHub Pages 发布目录：`main` 分支的 `/docs`。
