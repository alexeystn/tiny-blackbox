pyinstaller ../GUI/tinybb_gui.py --name="Tiny Blackbox" --windowed --onefile --add-data="..\resources\tiny_bb.ico;." --icon "../resources/tiny_bb.ico"
move ".\dist\Tiny Blackbox.exe" "Tiny Blackbox.exe"
rmdir ../GUI/__pycache__ /s /q
rmdir build /s /q
rmdir dist /s /q
del "Tiny Blackbox.spec"
:: replace ; with : for macOS
