## Tiny Blackbox
![Photo](tiny-blackbox.png)

Tiny Blackbox records all incoming serial data to the embedded flash memory.
Based on STM32F042 and Winbond W25Q128, as small as a microSD card.

* Size: 9 x 14 mm
* Weight: 0.47 g
* Data rate: 1.5 MBit/s
* Flash memory: 16 MB

### Setup
1) Connect device to any free UART port on your flight controller (note that logger’s TX should be connected to controller’s RX and vice versa).

![Pinout](pinout.png)

2) Configure Betaflight blackbox:
* Ports: Peripherals -> Blackbox logging, speed 1500000.
* Modes: Blackbox -> to any available AUX switch.
* Blackbox: Logging device -> Serial Port.

### Operating modes
* On power-up: Write mode (single slow blink if idle, fast blink if recording)
* Long button press: Read mode (double slow blink)
* One more long button press: Erase memory (fast blink)

### Read recorded logs
1) Configure `bf_uart_number number` in `config.json` to match blackbox port number in Betaflight.
2) Connect flight controller to PC.
3) Run Python script `blackbox_dump.py`. You may need to install `pyserial` module before. The script automatically switch your flight controller into _serialpassthrough_ mode.
4) Long press button on Tiny Blackbox when you are asked to. Device is switched to _Read_ mode, with LED double slow blink.
5) Wait until all blackbox data is copied to file.
