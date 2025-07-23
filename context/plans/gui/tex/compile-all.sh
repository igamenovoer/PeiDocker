#!/bin/bash

echo "======================================"
echo "PeiDocker GUI Design Documents"
echo "LaTeX Compilation Script (XeLaTeX)"
echo "======================================"
echo

echo "[1/5] Compiling gui-overview.tex..."
if ! xelatex gui-overview.tex; then
    echo "ERROR: Failed to compile gui-overview.tex"
    exit 1
fi

echo "[2/5] Compiling gui-simple-mode.tex..."
if ! xelatex gui-simple-mode.tex; then
    echo "ERROR: Failed to compile gui-simple-mode.tex"
    exit 1
fi

echo "[3/5] Compiling gui-advanced-mode.tex..."
if ! xelatex gui-advanced-mode.tex; then
    echo "ERROR: Failed to compile gui-advanced-mode.tex"
    exit 1
fi

echo "[4/5] Compiling gui-components.tex..."
if ! xelatex gui-components.tex; then
    echo "ERROR: Failed to compile gui-components.tex"
    exit 1
fi

echo "[5/5] Compiling gui-simple-mode-test.tex..."
if ! xelatex gui-simple-mode-test.tex; then
    echo "ERROR: Failed to compile gui-simple-mode-test.tex"
    exit 1
fi

echo
echo "======================================"
echo "SUCCESS: All documents compiled!"
echo "======================================"
echo
echo "Generated PDFs:"
echo "- gui-overview.pdf (4 pages) - Application architecture overview"
echo "- gui-simple-mode.pdf (9 pages) - Detailed wizard flow diagrams"
echo "- gui-advanced-mode.pdf (7 pages) - Form-based interface layout"
echo "- gui-components.pdf (17 pages) - Individual UI widget specifications"
echo "- gui-simple-mode-test.pdf (2 pages) - Test document for emoji support"
echo
echo "Total: 39 pages of comprehensive GUI design documentation"
echo