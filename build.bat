@echo off
echo ==============================================
echo BedrockCapsule 2.3 - Build Script
echo ==============================================

:: Find Python and PyInstaller
set "PYTHON_EXE="
set "PYINSTALLER_CMD="

python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
)

pyinstaller --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYINSTALLER_CMD=pyinstaller"
)

if not defined PYINSTALLER_CMD (
    for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%d\Scripts\pyinstaller.exe" (
            set "PYINSTALLER_CMD=%%d\Scripts\pyinstaller.exe"
            set "PYTHON_EXE=%%d\python.exe"
        )
    )
)

if not defined PYINSTALLER_CMD (
    echo.
    echo [ERROR] PyInstaller not found in PATH or in %LOCALAPPDATA%\Programs\Python!
    echo Please make sure you have installed it using 'pip install pyinstaller'.
    ping 127.0.0.1 -n 6 >nul
    exit /b 1
)

echo [1/3] Checking and installing required packages from requirements.txt...
if exist "requirements.txt" (
    if defined PYTHON_EXE (
        "%PYTHON_EXE%" -m pip install -r requirements.txt --quiet
    )
)

echo.
echo [2/3] Compiling Python executable with PyInstaller...
echo Using PyInstaller: %PYINSTALLER_CMD%
"%PYINSTALLER_CMD%" --clean -y BedrockCapsule_2.3.spec

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] PyInstaller failed to build the executable! Please check the errors above.
    ping 127.0.0.1 -n 6 >nul
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Packing Windows Installer with Inno Setup...
set "ISCC_CMD="
where ISCC >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "ISCC_CMD=ISCC"
) else (
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        set "ISCC_CMD=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
        set "ISCC_CMD=C:\Program Files\Inno Setup 6\ISCC.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
        set "ISCC_CMD=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
    )
)

if defined ISCC_CMD (
    if exist "setup.iss" (
        echo Using Inno Setup: "%ISCC_CMD%"
        "%ISCC_CMD%" setup.iss
        if errorlevel 1 (
            echo.
            echo [ERROR] Inno Setup failed to pack the installer!
            ping 127.0.0.1 -n 6 >nul
            exit /b 1
        )
    ) else (
        echo [INFO] setup.iss not found. Standalone executable ready in the "dist" folder!
    )
) else (
    echo.
    echo [WARNING] Inno Setup ISCC.exe was not found in PATH or standard Program Files.
    echo The installer step was skipped, but your standalone .exe is ready in the "dist" folder!
)

echo.
echo ==============================================
echo BUILD COMPLETE!
echo Your compiled .exe is in the "dist" folder.
echo Your setup installer is in the "Output" folder.
echo ==============================================
