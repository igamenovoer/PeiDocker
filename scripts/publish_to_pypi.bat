@echo off
REM Script to publish PeiDocker to PyPI (Windows)

echo PeiDocker PyPI Publication Script
echo =================================

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

REM Build the package
echo Building package...
python -m build
if %errorlevel% neq 0 exit /b %errorlevel%

REM Show what will be uploaded
echo Package contents:
dir dist

REM Ask for confirmation
echo.
set /p testpypi="Do you want to upload to TestPyPI first? (y/n): "

if /i "%testpypi%"=="y" (
    echo Uploading to TestPyPI...
    python -m twine upload --repository testpypi dist/*
    echo.
    echo Test installation with:
    echo   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pei-docker
    echo.
    set /p continue="Continue to upload to PyPI? (y/n): "
    if /i not "!continue!"=="y" (
        echo Aborted.
        exit /b 1
    )
)

REM Upload to PyPI
echo Uploading to PyPI...
python -m twine upload dist/*

echo.
echo Successfully published to PyPI!
echo Install with: pip install pei-docker