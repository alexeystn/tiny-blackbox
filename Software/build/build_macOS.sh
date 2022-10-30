#!/bin/bash
cd "../GUI"
pyinstaller "tinybb_gui.py" --name="Tiny_Blackbox" --windowed --onefile --icon "tinybb.icns"
rm "Tiny_Blackbox.spec"
