# Tiny Blackbox
<img src="Images/tiny-blackbox.png" width="500" />

Tiny Blackbox - open source ultra-light external logger for micro drones.<br>

* Size: 8 x 13 mm
* Weight: 0.32 g
* Logging rate: up to 8 kHz 
* Data rate: 1.5 Mbit/s
* Current consumption: < 30 mA
* Flash memory: 16 MB, W25Q128JVPIQ
* MCU: STM32G031G8U6

For previous version with F042 chip go to [this page](https://github.com/alexeystn/tiny-blackbox/tree/stm32f042)

## Setup
<img src="Images/pinout.png" width="250" />

1) Connect the device to any free UART port on your flight controller (RX->TX, TX->RX).
2) Setup blackbox in Betaflight Configurator:
* Ports tab: Peripherals -> Blackbox logging, speed 1500000.
* Modes tab: Blackbox -> assign to any available AUX switch.
* Blackbox tab: Logging device -> Serial Port.
<details>
<summary><b>Screenshots</b></summary>
<img src="Images/betaflight.png">
</details>

## Operating modes
<img src="Images/modes.png" width="700" />

## Read recorded logs
1) Download application on [Releases](https://github.com/alexeystn/tiny-blackbox/releases) page: "exe" for Windows, "app" for macOS.
2) Connect flight controller to PC.
3) Hold hardware button for 1 second to switch into Read mode (double blinks).
4) Open application, configure connection parameters and press "Connect".
5) Save logs to file and open them with Betaflight Blackbox Explorer.
<img src="Images/screenshot.png"  width="200" />

Also, you can connect Logger directly to PC with FTDI/CP2102 adapter, without flight controller. <br>
Select "Serial-USB adapter" instead of "Betaflight passthrough".

<details>
<summary><b>Optional: Run the source code</b></summary>
<br>
If you face some difficulties running exe/app, you can run GUI source code:

1) Get the latest version of [Python](https://www.python.org/downloads/). <br>
Set "Add Python to PATH" checkbox while installing.
2) Install additional modules. <br>
Open "cmd.exe" (Windows) or "Terminal" (macOS) and enter: <br>
`pip3 install pyserial` <br>
`pip3 install PyQt5==5.15`
3) Download and run GUI Python script: [tinybb_gui.py](https://raw.githubusercontent.com/alexeystn/tiny-blackbox/main/Software/GUI/tinybb_gui.py).
</details>

## For developers and enthusiasts

* PCB thickness 0.6 mm is optimum.
* Build firmware using [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html).
* Flash pre-built HEX-firmware with [STM32CubeProg](https://www.st.com/content/st_com/en/products/development-tools/software-development-tools/stm32-software-development-tools/stm32-programmers/stm32cubeprog.html) or [STLink](https://github.com/stlink-org/stlink) toolset.
* Connect ST-Link programmer to SWDIO and SWCLK pins:

<img src="Images/swd.png" width="250" />

## Contacts
 
Feel free to contact me in Telegram: [@AlexeyStn](https://t.me/AlexeyStn)
