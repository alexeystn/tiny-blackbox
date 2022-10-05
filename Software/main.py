import sys
import serial.tools.list_ports

from PyQt5.QtWidgets import (
    QWidget, QApplication, QGridLayout, QVBoxLayout, QSpacerItem,
    QPushButton, QComboBox, QLineEdit, QProgressBar, QLabel
)
from PyQt5.QtCore import Qt


def run():
    print("Run")


class Window(QWidget):

    connectionTypes = ['USB-Serial adapter', 'Betaflight passthrough']

    def __init__(self):
        super().__init__()

        self.comboBoxPort = QComboBox()
        self.comboBoxPort.addItems([c.device for c in serial.tools.list_ports.comports()])
        self.comboBoxPort.setFixedWidth(170)
        self.comboBoxType = QComboBox()
        self.comboBoxType.addItems(self.connectionTypes)
        self.comboBoxType.setFixedWidth(170)
        self.lineEditUart = QLineEdit('1')
        self.lineEditUart.setFixedWidth(170)
        self.lineEditBaud = QLineEdit('500000')
        self.lineEditBaud.setFixedWidth(170)
        self.buttonConnect = QPushButton('Connect')
        self.buttonErase = QPushButton('Erase')
        self.buttonSave = QPushButton('Save')
        self.labelStatus = QLabel('Logger not connected')
        self.labelStatus.setAlignment(Qt.AlignCenter)

        labelPort = QLabel('Port')
        labelType = QLabel('Type')
        labelBaud = QLabel('Baud')
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
        layoutConnection.addWidget(labelBaud, 2, 0, 1, 1)
        layoutConnection.addWidget(self.lineEditBaud, 2, 1, 1, 1)
        layoutConnection.addWidget(labelUart, 3, 0, 1, 1)
        layoutConnection.addWidget(self.lineEditUart, 3, 1, 1, 1)

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
        self.setWindowFlag(Qt.WindowCloseButtonHint)

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
        self.buttonConnect.clicked.connect(lambda run1: print("Run"))
        self.comboBoxType.activated.connect(self.handleTypeSelection)

        self.handleTypeSelection()

    def handleTypeSelection(self):
        if self.comboBoxType.currentText() == self.connectionTypes[0]:
            self.lineEditUart.setEnabled(True)
        else:
            self.lineEditUart.setEnabled(False)
        print('Changed')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.setFixedSize(window.size())
    sys.exit(app.exec())
