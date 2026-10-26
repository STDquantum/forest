@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

where java >nul 2>nul
if errorlevel 1 (
    echo 未找到 Java，请先安装 Java 并加入 PATH。
    goto failed
)
if defined APKTOOL_JAR (
    if not exist "%APKTOOL_JAR%" (
        echo APKTOOL_JAR 指定的文件不存在，请检查设置。
        goto failed
    )
) else (
    where apktool.bat >nul 2>nul
    if errorlevel 1 (
        echo 未找到 Apktool，请先将 apktool.bat 加入 PATH，或设置 APKTOOL_JAR。
        goto failed
    )
)

echo [1/2] 从官网下载最新 Forest 安卓 APK，请稍候……
call :python scripts\download_forest_apk.py
if errorlevel 1 goto failed

echo.
echo [2/2] 更新树种、树图、地皮和网页数据……
call :python main.py
if errorlevel 1 goto failed

echo.
echo 更新完成。重新打开或刷新网页即可查看。
exit /b 0

:failed
echo.
echo 更新失败，请检查上面的错误信息。
exit /b 1

:python
if defined PYTHON_HOME (
    "%PYTHON_HOME%\python.exe" %*
) else if exist "D:\conda\env3.10\python.exe" (
    "D:\conda\env3.10\python.exe" %*
) else (
    py -3 %*
)
exit /b %errorlevel%
