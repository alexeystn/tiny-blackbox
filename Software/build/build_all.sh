#!/bin/bash

VER="1.0.0"

cd ../GUI/

# Build executable for macOS
pyinstaller tinybb_gui.py --name="Tiny_Blackbox" --windowed --onefile --icon "tinybb.icns"

# Remove spec-file generated in previous step, 
# because it must not be used with Windows PyInstaller
rm Tiny_Blackbox.spec

# Run Windows PyInstaller in Docker
# This use "tinybb_gui_win.spec" file with removed "hooksconfig={}" line
# Option A: run public image from repository
## docker run --rm -v "$PWD":/src/ cdrx/pyinstaller-windows:python3
# Option B: run personal container with pre-installed dependencies
docker run --rm -v "$PWD":/src/ pyinstaller-windows

# Move executables to "output"
mkdir ../build/output
mv dist/windows/Tiny_Blackbox.exe "../build/output/Tiny_Blackbox_"$VER".exe"
mv dist/Tiny_Blackbox.app "../build/output/Tiny_Blackbox_"$VER".app"

# Remove temporary files
rm -r dist
rm -r __pycache__
rm -r build
