@echo off
echo ======================================
echo PeiDocker GUI Design Documents
echo LaTeX Compilation Script (XeLaTeX)
echo ======================================
echo.

echo [1/5] Compiling gui-overview.tex...
xelatex gui-overview.tex
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile gui-overview.tex
    pause
    exit /b 1
)

echo [2/5] Compiling gui-simple-mode.tex...
xelatex gui-simple-mode.tex
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile gui-simple-mode.tex
    pause
    exit /b 1
)

echo [3/5] Compiling gui-advanced-mode.tex...
xelatex gui-advanced-mode.tex
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile gui-advanced-mode.tex
    pause
    exit /b 1
)

echo [4/5] Compiling gui-components.tex...
xelatex gui-components.tex
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile gui-components.tex
    pause
    exit /b 1
)

echo [5/5] Compiling gui-simple-mode-test.tex...
xelatex gui-simple-mode-test.tex
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile gui-simple-mode-test.tex
    pause
    exit /b 1
)

echo.
echo ======================================
echo SUCCESS: All documents compiled!
echo ======================================
echo.
echo Generated PDFs:
echo - gui-overview.pdf (4 pages) - Application architecture overview
echo - gui-simple-mode.pdf (9 pages) - Detailed wizard flow diagrams
echo - gui-advanced-mode.pdf (7 pages) - Form-based interface layout
echo - gui-components.pdf (17 pages) - Individual UI widget specifications  
echo - gui-simple-mode-test.pdf (2 pages) - Test document for emoji support
echo.
echo Total: 39 pages of comprehensive GUI design documentation
echo.
pause