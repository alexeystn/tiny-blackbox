cd ../GUI
pyinstaller tinybb_gui.py --name="Tiny_Blackbox" --windowed --onefile --add-data="tinybb.ico;." --icon "tinybb.ico"
del "Tiny_Blackbox.spec"
