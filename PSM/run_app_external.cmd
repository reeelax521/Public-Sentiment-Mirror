@echo off
cd /d E:\undergraduate\Web\PSM
echo Starting Yuqing Mirror for LAN access...
echo.
echo This mode listens on 0.0.0.0:8501.
echo Other devices on the same network can visit:
echo   http://YOUR_COMPUTER_IP:8501
echo.
..\.venv\Scripts\python.exe -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
echo.
echo Streamlit has stopped. Press any key to close this window.
pause > nul
