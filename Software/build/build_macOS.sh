#!/bin/bash
pyinstaller ../GUI/tinybb_gui.py --name="Tiny Blackbox" --windowed --onefile --icon "../resources/tiny_bb.icns"
mv ./dist/Tiny\ Blackbox.app ./Tiny\ Blackbox.app
rm -r ../GUI/__pycache__
rm -r ./build
rm -r ./dist
rm Tiny\ Blackbox.spec
