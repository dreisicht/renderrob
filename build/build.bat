C:\Users\peter\AppData\Local\Programs\Python\Python38-32\Scripts\pyinstaller.exe --onefile --icon="C:\Users\peter\Documents\repositories\RenderRob\img\renderrob_icon.ico" C:\Users\peter\Documents\repositories\RenderRob\src\rr_master.py
xcopy /D ..\src\util\rr_denoisescript.py .\dist\util\rr_denoisescript.py
xcopy /D ..\src\util\rr_renderscript.py .\dist\util\rr_renderscript.py
xcopy /D ..\src\util\rr_user_commands.py .\dist\util\rr_user_commands.py
xcopy /D ..\key\ .\dist\key\
REM rr_master.exe in RenderRob.exe umbennen
