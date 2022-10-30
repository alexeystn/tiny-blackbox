#!/bin/bash
cd ../GUI/

# build executable for macOS
pyinstaller tinybb_gui.py --name="Tiny_Blackbox" --windowed --onefile --icon "tinybb.icns"

# remove spec-file generated in previous step
# it must not be used with Windows PyInstaller
rm Tiny_Blackbox.spec

# run Windows PyInstaller in Docker
# this use "tinybb_gui_win.spec" file with Windows parameters
# and removed "hooksconfig={}" line
docker run --rm -v "$PWD":/src/ cdrx/pyinstaller-windows:python3

# move executables to "output"
mkdir ../build/output
mv dist/windows/Tiny_Blackbox.exe ../build/output/Tiny_Blackbox.exe 
mv dist/Tiny_Blackbox.app ../build/output/Tiny_Blackbox.app 

# remove temporary files
rm -r dist
rm -r __pycache__
rm -r build
