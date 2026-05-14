@echo off
cd /d E:\undergraduate\Web\PSM
echo Starting Yuqing Mirror...
echo.
..\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
echo.
echo Streamlit has stopped. Press any key to close this window.
pause > nul
