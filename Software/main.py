import sys
import serial
import time
from datetime import datetime
import serial.tools.list_ports

from PyQt5.QtWidgets import (
    QWidget, QApplication, QGridLayout, QVBoxLayout, QSpacerItem,
    QPushButton, QComboBox, QLineEdit, QProgressBar, QLabel,
    QTextEdit, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QSettings, pyqtSignal, QThread


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


class SerialPort(QThread):

    status = ''
    progressUpdateSignal = pyqtSignal(dict)

    def __init__(self, config):
        QThread.__init__(self)
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
            percents = None
            try:
                percents = float(line.split(sep='%')[0].split(sep=' ')[-1])
                line = 'Logger connected'
            except:
                line = 'Cannot decode response'
            finally:
                self.status = (line, percents)
        else:
            self.status = ('No response from Blackbox', None)

    def erase(self):
        self.instance.write('erase\n'.encode())

    def save(self, params):
        filename = params['filename']
        percents = params['percents']
        progress = {'text': 'Downloading', 'size': '0 kB', 'bar': 0}
        self.progressUpdateSignal.emit(progress)
        self.instance.write('read\n'.encode())
        f = open(filename, 'wb')
        rx_counter = 0
        rx_counter_scaled_prev = 0
        full_size = 16*1024*1024
        print('Downloading:')
        print('Press ctrl+c to stop')

        while True:  # print dots and megabytes
            d = self.instance.read(10000)
            if len(d) > 0:
                rx_counter += len(d)
                f.write(d)
                rx_counter_scaled = rx_counter // (2 ** 15)
                if rx_counter_scaled > rx_counter_scaled_prev:
                    progress['size'] = '{0:.1f} Mb'.format(rx_counter / (2 ** 20))
                    progress['bar'] = 100 * rx_counter / (full_size * percents / 100)
                    self.progressUpdateSignal.emit(progress)
                    print('.', end='', flush=True)
                    f.flush()
                    if rx_counter_scaled % 16 == 0:
                        print('{0:.0f} Mb'.format(rx_counter / (2 ** 20)))
                    rx_counter_scaled_prev = rx_counter_scaled
            else:
                break
        f.close()
        progress['text'] = 'Saved'
        progress['size'] = '{0:.1f} Mb'.format(rx_counter / (2 ** 20))
        progress['bar'] = 100
        print('\n' + str(rx_counter) + ' bytes received')
        print(f.name + ' saved')

    def close(self):
        self.instance.close()

    def updateStatus(self):
        return


class Window(QWidget):

    connectionTypes = ['USB-Serial adapter', 'Betaflight passthrough']
    isConnected = False
    saveLogSignal = pyqtSignal(dict)

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
        self.progressBarMemory.setValue(0)
        self.progressBarMemory.setAlignment(Qt.AlignCenter)
        self.progressBarMemory.setStyleSheet("QProgressBar { border: 1px solid; \
                                        text-align: center; } QProgressBar::chunk \
                                        {background-color: #77BBFF; width: 1px;}")
        self.progressBarMemory.setFormat('')

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
            self.setTabOrder(self.comboBoxType, self.lineEditUart)
            self.setTabOrder(self.lineEditUart, self.buttonConnect)
            self.buttonConnect.setDefault(True)
            self.setFocusPolicy(Qt.ClickFocus)

        self.buttonConnect.setFocus()
        self.buttonConnect.clicked.connect(self.buttonConnectPress)
        self.comboBoxType.activated.connect(self.handleTypeSelection)
        self.buttonErase.clicked.connect(self.buttonErasePress)
        self.buttonSave.clicked.connect(self.buttonSavePress)
        self.handleTypeSelection()
        self.previousPorts = []
        self.serialPort = None
        self.updatePorts()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePorts)
        self.timer.start(1000)
        self.percents = 100

    def buttonErasePress(self):
        if self.isConnected:
            button = QMessageBox.question(self, 'Blackbox', "Do you want to erase flash?")
            if button == QMessageBox.Yes:
                self.serialPort.erase()
                QMessageBox.information(self, 'Blackbox', 'Wait ~30s until LED is blinking')
                self.isConnected = False
                self.labelStatus.setText('')
                self.progressBarMemory.setValue(0)
                self.progressBarMemory.setFormat('')
                self.serialPort.close()

    def buttonSavePress(self):
        if self.isConnected:
            filename = QFileDialog.getSaveFileName(self, 'Save file',
                                                   datetime.now().strftime('Blackbox_%Y%m%d_%H%M%S.bbl'))[0]
            self.saveLogSignal.connect(self.serialPort.save)
            # self.serialPort.save(filename, self.percents)
            self.progressBarMemory.setValue(0)
            self.progressBarMemory.setFormat('')
            self.saveLogSignal.emit({'filename': filename, 'percents': self.percents})

    def progressBarUpdate(self, progress):
        self.labelStatus.setText(progress['text'])
        self.progressBarMemory.setValue(progress['bar'])
        self.progressBarMemory.setFormat(progress['size'])

    def buttonConnectPress(self):
        if self.comboBoxPort.currentText() == '':
            self.labelStatus.setText('Port not selected')
            return
        if self.comboBoxType.currentIndex() == 1:
            if not self.lineEditUart.text().isnumeric():
                self.labelStatus.setText('Incorrect UART')
                return
        self.settings.currentConfig['port'] = self.comboBoxPort.currentText()
        self.settings.currentConfig['type'] = self.comboBoxType.currentIndex()
        if self.comboBoxType.currentIndex() == 1:
            self.settings.currentConfig['uart'] = int(self.lineEditUart.text())
        self.settings.save()
        if self.isConnected:
            print('Already connected')
            return
        print('Connecting:', self.settings.currentConfig)
        self.serialPort = SerialPort(self.settings.currentConfig)
        self.serialPort.progressUpdateSignal.connect(self.progressBarUpdate)
        self.serialPort.start()
        if self.serialPort:
            if self.settings.currentConfig['type']:  # use passthrough
                print('Entering passthrough')
                self.labelStatus.setText('Passthrough')
                self.serialPort.bf_enable_passthrough(self.settings.currentConfig)
            self.serialPort.get_info()
            self.isConnected = True
            self.labelStatus.setText(self.serialPort.status[0])
            if not self.serialPort.status[1] is None:
                self.isConnected = True
                self.percents = self.serialPort.status[1]
                self.progressBarMemory.setValue(int(self.serialPort.status[1]))
                self.progressBarMemory.setFormat('{0:.1f}%'.format(self.serialPort.status[1]))
            else:
                self.serialPort.close()
                self.progressBarMemory.setValue(0)
                self.progressBarMemory.setFormat('')
                self.isConnected = False
        else:
            self.isConnected = False
            self.labelStatus.setText('Cannot connect')
            self.progressBarMemory.setValue(0)
            self.progressBarMemory.setFormat('No blackbox')

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
                self.progressBarMemory.setValue(0)
                self.progressBarMemory.setFormat('')

    def handleTypeSelection(self):
        if self.comboBoxType.currentText() == self.connectionTypes[0]:
            self.lineEditUart.setEnabled(False)
        else:
            self.lineEditUart.setEnabled(True)

    def closeEvent(self, event):
        if self.serialPort:
            self.serialPort.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.setFixedSize(window.size())
    sys.exit(app.exec())
