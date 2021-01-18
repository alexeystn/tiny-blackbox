## Tiny Blackbox
![Photo](tiny-blackbox.png)

Tiny Blackbox is an external ultra-light logger for micro drones.

This device records all incoming serial data to the embedded flash memory.

Based on STM32F042 and W25Q128 chips.

* Size: 9 x 14 mm
* Weight: 0.47 g
* Data rate: 1.5 Mbit/s
* Flash memory: 16 MB

### Setup
1) Connect the device to any free UART port on your flight controller (RX-TX, TX-RX).

![Pinout](pinout.png)

2) Setup blackbox in Betaflight configurator:
* Ports: Peripherals -> Blackbox logging, speed 1500000.
* Modes: Blackbox -> assign to any available AUX switch.
* Blackbox: Logging device -> Serial Port.

### Operating modes
|Mode| Action  | Description | LED|
| --- | :---: | --- | --- |
|Write| Default on Power-up           | Write RX data to flash at 1.5 Mbit/s | Single slow blink - no data <br/>Fast blink - recording|
|Read | Long 1s button press          | Dump all flash content at 500 kbit/s |  Double slow blink<br/>|
|Erase| One more long 3s button press | Erase memory    |  Fast blink<br/> |

### Read recorded logs
1) Configure `bf_uart_number` number in `config.json` to match blackbox port number in Betaflight.
2) Connect flight controller to PC.
3) Run Python script `blackbox_dump.py`. You may need to install `pyserial` module before. The script automatically switches your flight controller into _Serial Passthrough_ mode.
4) Hold button for 1 second to switch device into Read mode.
5) Wait until all blackbox data is saved to file.
6) Open file with Blackbox Explorer and enjoy :-)
