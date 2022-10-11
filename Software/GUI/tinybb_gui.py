import sys
import os
import serial
import time
from datetime import datetime
import serial.tools.list_ports

from PyQt5.QtWidgets import (
    QWidget, QApplication, QGridLayout, QVBoxLayout, QSpacerItem,
    QPushButton, QComboBox, QLineEdit, QProgressBar, QLabel,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QSettings, pyqtSignal, QThread, QObject


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
        defaultConfig = {'port': 'COM1', 'type': 0, 'uart': 1, 'directory': ''}
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


class SerialThread(QObject):

    progressValueSignal = pyqtSignal(int)
    progressTextSignal = pyqtSignal(str)
    statusTextSignal = pyqtSignal(str)
    connectionStatusSignal = pyqtSignal(bool)

    name = None
    instance = None
    isConnected = None
    memoryUsedPercents = 100

    def setConnectionStatus(self, status):
        self.isConnected = status
        self.connectionStatusSignal.emit(status)

    def connectToPort(self, config):
        self.statusTextSignal.emit('Connecting')
        self.name = config['port']
        self.instance = serial.Serial(self.name, baudrate=500000, timeout=1)  # + param
        if config['type']:
            self.statusTextSignal.emit('Switching to Passthrough')
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
        self.getInfo()

    def getInfo(self):
        self.instance.flushInput()
        self.instance.write('\n'.encode())
        time.sleep(0.1)
        self.instance.write('info\n'.encode())
        resp = self.instance.readline()
        if len(resp) > 0:
            line = resp.decode().strip()
            percents = 0
            try:
                percents = float(line.split(sep='%')[0].split(sep=' ')[-1])
                line = 'Logger connected'
                self.memoryUsedPercents = percents
            except:
                line = 'Cannot decode response'
            finally:
                self.progressValueSignal.emit(int(percents))
                self.progressTextSignal.emit('{0:.1f}% used'.format(percents))
                self.statusTextSignal.emit(line)
                self.setConnectionStatus(True)
        else:
            self.disconnectFromPort()
            self.statusTextSignal.emit('No response from Blackbox')
            self.progressValueSignal.emit(0)
            self.progressTextSignal.emit('')

    def saveToFile(self, filename):
        if not self.isConnected:
            return
        percents = self.memoryUsedPercents
        self.progressValueSignal.emit(0)
        self.statusTextSignal.emit('Downloading')
        self.instance.write('read\n'.encode())
        f = open(filename, 'wb')
        rx_counter = 0
        rx_counter_scaled_prev = 0
        full_size = 16 * 1024 * 1024
        while True:  # print dots and megabytes
            d = self.instance.read(10000)
            if len(d) > 0:
                rx_counter += len(d)
                f.write(d)
                rx_counter_scaled = rx_counter // (2 ** 15)
                if rx_counter_scaled > rx_counter_scaled_prev:
                    self.progressTextSignal.emit('{0:.1f} Mb'.format(rx_counter / (2 ** 20)))
                    self.progressValueSignal.emit(round(100 * rx_counter / (full_size * percents / 100)))
                    print('.', end='', flush=True)
                    f.flush()
                    if rx_counter_scaled % 32 == 0:
                        print('{0:.0f} Mb'.format(rx_counter / (2 ** 20)))
                    rx_counter_scaled_prev = rx_counter_scaled
            else:
                break
        f.close()
        self.progressValueSignal.emit(100)
        self.progressTextSignal.emit('{0:.1f} Mb saved'.format(rx_counter / (2 ** 20)))
        self.statusTextSignal.emit('Done')
        print('\n' + str(rx_counter) + ' bytes received')
        print(f.name + ' saved')

    def eraseFlash(self):
        if not self.isConnected:
            return
        self.instance.write('erase\n'.encode())
        erasingTotalTime = 40
        startTime = time.time()
        self.progressTextSignal.emit('')
        self.progressValueSignal.emit(0)
        self.statusTextSignal.emit('Erasing')
        while True:
            elapsedTime = time.time() - startTime
            progress = elapsedTime / erasingTotalTime * 100
            self.progressValueSignal.emit(round(progress))
            self.progressTextSignal.emit('0:{0:02.0f}'.format(elapsedTime))
            res = self.instance.readline()
            res = res.decode().strip()
            if len(res) == 0:
                self.statusTextSignal.emit('Failed')
                self.progressTextSignal.emit('')
                self.progressValueSignal.emit(0)
                break
            if res == 'Done':
                self.statusTextSignal.emit('Done')
                self.progressTextSignal.emit('')
                self.progressValueSignal.emit(0)
                break

    def disconnectFromPort(self):
        self.instance.close()
        self.statusTextSignal.emit('Disconnected')
        self.progressTextSignal.emit('')
        self.progressValueSignal.emit(0)
        self.setConnectionStatus(False)


class Window(QWidget):

    connectionTypes = ['USB-Serial adapter', 'Betaflight passthrough']
    startConnectionSignal = pyqtSignal(dict)
    stopConnectionSignal = pyqtSignal()
    saveLogToFileSignal = pyqtSignal(str)
    eraseFlashSignal = pyqtSignal()

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

        self.thread = QThread()
        self.worker = SerialThread()
        self.worker.moveToThread(self.thread)
        self.worker.progressValueSignal.connect(self.updateProgressValue)
        self.worker.progressTextSignal.connect(self.updateProgressText)
        self.worker.statusTextSignal.connect(self.updateStatusText)
        self.worker.connectionStatusSignal.connect(self.applyConnectionStatus)
        self.startConnectionSignal.connect(self.worker.connectToPort)
        self.stopConnectionSignal.connect(self.worker.disconnectFromPort)
        self.saveLogToFileSignal.connect(self.worker.saveToFile)
        self.eraseFlashSignal.connect(self.worker.eraseFlash)
        self.thread.start()
        self.applyConnectionStatus(False)

        self.previousPorts = []
        self.updatePorts()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePorts)
        self.timer.start(1000)
        self.percents = 100

    def updateProgressValue(self, value):
        self.progressBarMemory.setValue(int(value))

    def updateProgressText(self, text):
        self.progressBarMemory.setFormat(text)

    def updateStatusText(self, text):
        self.labelStatus.setText(text)

    def applyConnectionStatus(self, status):
        self.buttonErase.setEnabled(status)
        self.buttonSave.setEnabled(status)
        if status:
            self.buttonConnect.setText('Disconnect')
        else:
            self.buttonConnect.setText('Connect')

    def buttonErasePress(self):
        button = QMessageBox.question(self, 'Tiny Blackbox', "Do you want to erase flash?")
        if button == QMessageBox.Yes:
            self.eraseFlashSignal.emit()

    def buttonSavePress(self):
        lastDirectory = self.settings.currentConfig['directory']
        newFilename = datetime.now().strftime('Blackbox_%Y%m%d_%H%M%S.bbl')
        newPath = os.path.join(lastDirectory, newFilename)
        filename = QFileDialog.getSaveFileName(self, 'Save file', newPath)[0]
        if filename != '':
            self.settings.currentConfig['directory'] = os.path.split(filename)[0]
            self.saveLogToFileSignal.emit(filename)
            self.settings.save()

    def buttonConnectPress(self):
        if self.worker.isConnected:
            self.stopConnectionSignal.emit()
            return
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
        self.startConnectionSignal.emit(self.settings.currentConfig)

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
        if self.worker.isConnected:
            if self.worker.name not in portList:
                self.stopConnectionSignal.emit()

    def handleTypeSelection(self):
        if self.comboBoxType.currentText() == self.connectionTypes[0]:
            self.lineEditUart.setEnabled(False)
        else:
            self.lineEditUart.setEnabled(True)

    def closeEvent(self, event):
        if self.worker.isConnected:
            self.stopConnectionSignal.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.setFixedSize(window.size())
    sys.exit(app.exec())
