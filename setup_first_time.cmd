@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [首次安裝] 安裝圖卡引擎需要的 Python 套件與瀏覽器元件（只做一次，需要網路，約 150MB）
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% -c "import sys;sys.exit(0 if sys.version_info >= (3,10) else 1)" || goto :nopy
%PY% -m pip install -r requirements.txt || goto :err
%PY% -m playwright install chromium || goto :err
echo.
echo 安裝完成。之後請直接雙擊 start_windows.cmd
pause
exit /b 0
:nopy
echo 找不到 Python 3.10 以上版本。請依公司核准方式安裝 Python，再重新執行本檔。
pause
exit /b 1
:err
echo.
echo 安裝失敗。請把這個視窗的畫面截圖回傳（不含任何客戶資料）。
echo 若公司網路擋住下載，可先在家裡電腦安裝並出圖，再用「下載完整備份／還原備份」把案件搬過去。
pause
exit /b 1
