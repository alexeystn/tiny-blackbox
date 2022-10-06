import sys
import serial
import time
import serial.tools.list_ports

from PyQt5.QtWidgets import (
    QWidget, QApplication, QGridLayout, QVBoxLayout, QSpacerItem,
    QPushButton, QComboBox, QLineEdit, QProgressBar, QLabel
)
from PyQt5.QtCore import Qt, QTimer, QSettings, pyqtSignal


def run():
    print("Run")


class Settings(QSettings):

    currentConfig = {}

    def __init__(self):
        super().__init__("AlexeyStn", "TinyBlackbox")
        self.load()

    def load(self):
        """
        1) macOS - settings are stored in file: ~/Library/Preferences/com.alexeystn.TinyBlackbox.plist
        Use command 'killall -u $USER cfprefsd' to reload settings
        2) Windows - settings are stored in system registry: /HKEY_CURRENT_USER/Software/AlexeyStn/TinyBlackbox
        """
        defaultConfig = {'port': 'COM1', 'type': 0, 'uart': 1}
        success = True
        for item in defaultConfig:
            value = self.value(item)
            if value is None:
                success = False
            else:
                self.currentConfig[item] = value
        if success:
            print('Load: OK')
            print(self.currentConfig)
        else:
            self.currentConfig = defaultConfig.copy()
            print('Load: FAIL')
            self.save()

    def save(self):
        for item in self.currentConfig:
            self.setValue(item, self.currentConfig[item])


class SerialPort:

    status = ''

    def __init__(self, config):
        self.name = config['port']
        self.instance = serial.Serial(self.name, baudrate=500000, timeout=1)  # + param
        # self.use_passthrough = config['type']
        print(self.instance)

    def bf_enable_passthrough(self, config):
        print('===== Betaflight CLI mode =====')
        self.instance.write(b'#\n')
        self.instance.readline()
        request_str = 'serialpassthrough ' + \
                      str(config['uart'] - 1) + ' ' + \
                      str(500000) + '\n'
        self.instance.write(request_str.encode())
        while True:
            res = self.instance.readline()
            if len(res) == 0:
                break
            s = res.decode().strip()
            if len(s) > 0:
                print(' >> ' + s)
        print('==============================')

    def get_info(self):
        self.instance.flushInput()
        self.instance.write('\n'.encode())
        time.sleep(0.1)
        self.instance.write('info\n'.encode())
        resp = self.instance.readline()
        print(resp)
        if len(resp) > 0:
            line = resp.decode().strip()
            percents = 0
            try:
                percents = float(line.split(sep='%')[0].split(sep=' ')[-1])
            except:
                line = 'Cannot decode response'
            finally:
                self.status = (line, percents)
        else:
            self.status = ('No response from Blackbox', 0)

    def close(self):
        self.instance.close()

    def updateStatus(self):
        return


class Window(QWidget):

    connectionTypes = ['USB-Serial adapter', 'Betaflight passthrough']
    isConnected = False

    def __init__(self):
        super().__init__()
        self.settings = Settings()

        self.comboBoxPort = QComboBox()
        self.comboBoxPort.setFixedWidth(170)
        self.comboBoxType = QComboBox()
        self.comboBoxType.addItems(self.connectionTypes)
        self.comboBoxType.setCurrentIndex(self.settings.currentConfig['type'])
        self.comboBoxType.setFixedWidth(170)
        self.lineEditUart = QLineEdit(str(self.settings.currentConfig['uart']))
        self.lineEditUart.setFixedWidth(170)
        self.buttonConnect = QPushButton('Connect')
        self.buttonErase = QPushButton('Erase')
        self.buttonSave = QPushButton('Save')
        self.labelStatus = QLabel('Disconnected')
        self.labelStatus.setAlignment(Qt.AlignCenter)

        labelPort = QLabel('Port')
        labelType = QLabel('Type')
        labelUart = QLabel('UART')

        self.progressBarMemory = QProgressBar()
        self.progressBarMemory.setRange(0, 100)
        self.progressBarMemory.setValue(35)
        self.progressBarMemory.setAlignment(Qt.AlignCenter)
        self.progressBarMemory.setStyleSheet("QProgressBar { border: 1px solid; \
                                        text-align: center; } QProgressBar::chunk \
                                        {background-color: #77BBFF; width: 1px;}")
        self.progressBarMemory.setFormat("35.5%")

        layoutConnection = QGridLayout()
        layoutConnection.addWidget(labelPort, 0, 0, 1, 1)
        layoutConnection.addWidget(self.comboBoxPort, 0, 1, 1, 1)
        layoutConnection.addWidget(labelType, 1, 0, 1, 1)
        layoutConnection.addWidget(self.comboBoxType, 1, 1, 1, 1)
        layoutConnection.addWidget(labelUart, 2, 0, 1, 1)
        layoutConnection.addWidget(self.lineEditUart, 2, 1, 1, 1)

        layoutActions = QGridLayout()
        layoutActions.addWidget(self.buttonConnect, 0, 0, 1, 2)
        layoutActions.addWidget(self.buttonErase, 1, 0, 1, 1)
        layoutActions.addWidget(self.buttonSave, 1, 1, 1, 1)

        layoutStatus = QVBoxLayout()
        layoutStatus.addWidget(self.labelStatus)
        layoutStatus.addWidget(self.progressBarMemory)

        layout = QVBoxLayout()
        layout.addLayout(layoutConnection)
        layout.addItem(QSpacerItem(100, 10))
        layout.addLayout(layoutStatus)
        layout.addItem(QSpacerItem(100, 10))
        layout.addLayout(layoutActions)

        self.setWindowTitle("Tiny Blackbox")
        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)

        if sys.platform.startswith('win'):
            self.setTabOrder(self.buttonConnect, self.buttonErase)
            self.setTabOrder(self.buttonErase, self.buttonSave)
            self.setTabOrder(self.buttonSave, self.comboBoxPort)
            self.setTabOrder(self.comboBoxPort, self.comboBoxType)
            self.setTabOrder(self.comboBoxType, self.lineEditBaud)
            self.setTabOrder(self.lineEditBaud, self.lineEditUart)
            self.setTabOrder(self.lineEditUart, self.buttonConnect)
            self.buttonConnect.setDefault(True)
            self.setFocusPolicy(Qt.ClickFocus)

        self.buttonConnect.setFocus()
        self.buttonConnect.clicked.connect(self.buttonConnectPress)
        self.comboBoxType.activated.connect(self.handleTypeSelection)

        self.handleTypeSelection()
        self.previousPorts = []
        self.serialPort = None
        self.updatePorts()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePorts)
        self.timer.start(1000)

    def buttonConnectPress(self):
        self.settings.currentConfig['port'] = self.comboBoxPort.currentText()
        self.settings.currentConfig['type'] = int(self.comboBoxType.currentIndex())
        self.settings.currentConfig['uart'] = int(self.lineEditUart.text())
        self.settings.save()
        print('Connecting:', self.settings.currentConfig)
        self.serialPort = SerialPort(self.settings.currentConfig)
        if self.serialPort:
            if self.settings.currentConfig['type']:  # use passthrough
                print('Entering passthrough')
                self.labelStatus.setText('Passthrough')
                self.serialPort.bf_enable_passthrough(self.settings.currentConfig)
            self.serialPort.get_info()
            self.isConnected = True
            self.labelStatus.setText(self.serialPort.status[0])
            self.progressBarMemory.setValue(int(self.serialPort.status[1]))
            self.progressBarMemory.setFormat('{0:.1f}%'.format(self.serialPort.status[1]))
        else:
            self.isConnected = False
            self.labelStatus.setText('Cannot connect')
            self.progressBarMemory.setValue(0)
            self.progressBarMemory.setFormat('')

    def updatePorts(self):
        portList = [c.device for c in serial.tools.list_ports.comports()]
        portList.sort()
        if portList == self.previousPorts:  # no changes
            return
        self.previousPorts = portList
        self.comboBoxPort.clear()
        self.comboBoxPort.addItems(portList)
        if self.settings.currentConfig['port'] in portList:
            self.comboBoxPort.setCurrentText(self.settings.currentConfig['port'])
        if self.isConnected:
            if self.serialPort.name not in portList:
                self.serialPort.close()
                self.isConnected = False
                self.labelStatus.setText('Connection lost')

    def handleTypeSelection(self):
        if self.comboBoxType.currentText() == self.connectionTypes[0]:
            self.lineEditUart.setEnabled(False)
        else:
            self.lineEditUart.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.setFixedSize(window.size())
    sys.exit(app.exec())
