cd ../GUI
pyinstaller tinybb_gui.py --name="Tiny_Blackbox" --windowed --onefile --add-data="tiny_bb.ico;." --icon "tiny_bb.ico"
del "Tiny_Blackbox.spec"
