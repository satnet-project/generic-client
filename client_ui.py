# coding=utf-8
import os
import misc
import time
import configurationWindow

from PyQt4 import QtGui, QtCore
from twisted.python import log

from gs_interface import GroundStationInterface

# FIXME import sentence no optimized
import client_amp
from threads import Threads

"""
   Copyright 2016 Samuel Góngora García
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
:Author:
    Samuel Góngora García (s.gongoragarcia@gmail.com)
"""
__author__ = 's.gongoragarcia@gmail.com'


class SatNetUI(QtGui.QWidget):
    def __init__(self, argumentsdict, parent=None):
        QtGui.QWidget.__init__(self, parent)
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 18))

        self.enviromentDesktop = os.environ.get('DESKTOP_SESSION')

        self.connection = ''

        self.initUI()
        self.initButtons()
        self.initFields()
        self.setParameters()
        self.initLogo()
        self.initConfiguration()
        self.initConsole()

        #  Use a dict for passing arg.
        self.setArguments(argumentsdict)

        self.gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo",
                                          client_amp.ClientProtocol)

        self.threads = Threads(self.CONNECTION_INFO, self.gsi)

        # Initialize the reactor parameters needed for the pyqt enviroment
        client_amp.Client(self.CONNECTION_INFO, self.gsi, self.threads).createconnection(test=False)


    # Create a new connection by loading the connection parameters
    # from the interface window
    def NewConnection(self, test=False):
        self.CONNECTION_INFO['username'] = str(self.LabelUsername.text())
        self.CONNECTION_INFO['password'] = str(self.LabelPassword.text())
        self.CONNECTION_INFO['connection'] =\
            str(self.LabelConnection.currentText())

        self.ButtonNew.setEnabled(False)
        self.ButtonCancel.setEnabled(True)
        self.LoadDefaultSettings.setEnabled(False)
        self.AutomaticReconnection.setEnabled(False)

        return client_amp.Client(self.CONNECTION_INFO, self.gsi,
                                 self.threads).setconnection(test=False)

    def initUI(self):
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.setFixedSize(1300, 800)
        self.setWindowTitle("SatNet client - %s" %
                            (self.CONNECTION_INFO['name']))

        if self.CONNECTION_INFO['parameters'] == 'yes':
            self.LoadParameters()
        elif self.CONNECTION_INFO['parameters'] == 'no':
            pass
        else:
            log.msg("No parameters configuration found." +
                    " Using default parameter - Yes")

    def initButtons(self):
        buttons = QtGui.QGroupBox(self)
        grid = QtGui.QGridLayout(buttons)
        buttons.setLayout(grid)

        self.ButtonNew = QtGui.QPushButton("Connection")
        self.ButtonNew.setToolTip("Start a new connection using " +
                                  " the selected connection")
        self.ButtonNew.setFixedWidth(145)
        self.ButtonNew.clicked.connect(self.NewConnection)
        self.ButtonCancel = QtGui.QPushButton("Disconnection")
        self.ButtonCancel.setToolTip("End current connection")
        self.ButtonCancel.setFixedWidth(145)
        self.ButtonCancel.clicked.connect(self.CloseConnection)
        self.ButtonCancel.setEnabled(False)
        self.ButtonLoad = QtGui.QPushButton("Load parameters from file")
        self.ButtonLoad.setToolTip("Load parameters from <i>.settings</i> file")
        self.ButtonLoad.setFixedWidth(296)
        self.ButtonLoad.clicked.connect(self.UpdateFields)
        self.ButtonConfiguration = QtGui.QPushButton("Configuration")
        self.ButtonConfiguration.setToolTip("Open configuration window")
        self.ButtonConfiguration.setFixedWidth(145)
        self.ButtonConfiguration.clicked.connect(self.SetConfiguration)
        ButtonHelp = QtGui.QPushButton("Help")
        ButtonHelp.setToolTip("Click for help")
        ButtonHelp.setFixedWidth(145)
        ButtonHelp.clicked.connect(self.usage)
        grid.addWidget(self.ButtonNew, 0, 0, 1, 1)
        grid.addWidget(self.ButtonCancel, 0, 1, 1, 1)
        grid.addWidget(self.ButtonLoad, 1, 0, 1, 2)
        grid.addWidget(self.ButtonConfiguration, 2, 0, 1, 1)
        grid.addWidget(ButtonHelp, 2, 1, 1, 1)
        buttons.setTitle("Connection")
        buttons.move(10, 10)

        self.dialogTextBrowser = configurationWindow.ConfigurationWindow(self)

    def initFields(self):
        # Connection parameters group
        connectionParameters = QtGui.QGroupBox(self)
        gridConnection = QtGui.QFormLayout()
        connectionParameters.setLayout(gridConnection)

        LabelAttemps = QtGui.QLabel("Reconnection tries:")
        LabelAttemps.setFixedWidth(145)
        self.FieldLabelAttemps = QtGui.QLineEdit()
        self.FieldLabelAttemps.setFixedWidth(145)
        gridConnection.addRow(LabelAttemps, self.FieldLabelAttemps)

        connectionParameters.setTitle("Connection parameters")
        connectionParameters.move(10, 140)
        # Configuration group.
        configuration = QtGui.QGroupBox(self)
        configurationLayout = QtGui.QVBoxLayout()
        configuration.setLayout(configurationLayout)

        self.LoadDefaultSettings =\
            QtGui.QCheckBox("Automatically load settings from file")
        configurationLayout.addWidget(self.LoadDefaultSettings)
        self.AutomaticReconnection =\
            QtGui.QCheckBox("Reconnect after a failure")
        configurationLayout.addWidget(self.AutomaticReconnection)

        configuration.move(10, 180)

        # User parameters group
        parameters = QtGui.QGroupBox(self)
        self.layout = QtGui.QFormLayout()
        parameters.setLayout(self.layout)

        self.LabelUsername = QtGui.QLineEdit()
        self.LabelUsername.setFixedWidth(190)
        self.layout.addRow(QtGui.QLabel("Username:       "),
                           self.LabelUsername)
        self.LabelPassword = QtGui.QLineEdit()
        self.LabelPassword.setFixedWidth(190)
        self.LabelPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.layout.addRow(QtGui.QLabel("Password:       "),
                           self.LabelPassword)

        self.LabelConnection = QtGui.QComboBox()
        self.LabelConnection.setFixedWidth(190)
        self.LabelConnection.addItems(['serial', 'udp', 'tcp', 'none'])
        self.LabelConnection.activated.connect(self.openInterface)
        self.layout.addRow(QtGui.QLabel("Interface:     "),
                           self.LabelConnection)

        parameters.setTitle("User data")
        parameters.move(10, 265)

        # User interface group
        interfaceControl = QtGui.QGroupBox(self)
        gridControl = QtGui.QGridLayout(interfaceControl)
        interfaceControl.setLayout(gridControl)

        self.stopInterfaceButton = QtGui.QPushButton("Stop interface")
        self.stopInterfaceButton.setToolTip("Stop the actual interface")
        self.stopInterfaceButton.setFixedWidth(145)
        self.stopInterfaceButton.clicked.connect(self.stopInterface)
        self.stopInterfaceButton.setEnabled(False)

        gridControl.addWidget(self.stopInterfaceButton, 0, 0, 1, 1)

        interfaceControl.move(155, 380)

    def initLogo(self):
        LabelLogo = QtGui.QLabel(self)
        LabelLogo.move(20, 450)

        pic = QtGui.QPixmap(os.getcwd() + "/logo.png")

        pic = pic.scaledToWidth(300)

        # pic = pic.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        LabelLogo.setPixmap(pic)
        LabelLogo.show()

    def initConfiguration(self):
        if self.CONNECTION_INFO['reconnection'] == 'yes':
            self.AutomaticReconnection.setChecked(True)
        elif self.CONNECTION_INFO['reconnection'] == 'no':
            self.AutomaticReconnection.setChecked(False)
        if self.CONNECTION_INFO['parameters'] == 'yes':
            self.LoadDefaultSettings.setChecked(True)
        elif self.CONNECTION_INFO['parameters'] == 'no':
            self.LoadDefaultSettings.setChecked(False)

    def initConsole(self):
        self.console = QtGui.QTextBrowser(self)
        self.console.move(340, 10)
        self.console.resize(950, 780)
        self.console.setFont(QtGui.QFont('SansSerif', 11))

    # Set parameters form arguments list.
    def setArguments(self, argumentsdict):
        if argumentsdict['username'] != "":
            self.LabelUsername.setText(argumentsdict['username'])
        if argumentsdict['connection'] != "":
            index = self.LabelConnection.findText(argumentsdict['connection'])
            self.LabelConnection.setCurrentIndex(index)

    # Set parameters from CONNECTION_INFO dict.
    def setParameters(self):
        self.FieldLabelAttemps.setText(self.CONNECTION_INFO['attempts'])
        self.LabelUsername.setText(self.CONNECTION_INFO['username'])

        try:
            index = self.LabelConnection.findText(
                self.CONNECTION_INFO['connection'])
            self.LabelConnection.setCurrentIndex(index)
        except Exception as e:
            log.err(e)

    def CloseConnection(self):
        self.gsi.clear_slots()

        self.ButtonNew.setEnabled(True)
        self.ButtonCancel.setEnabled(False)

    def UpdateFields(self):
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')

        log.msg("Parameters loaded from .setting file.")

    # Load connection parameters from .settings file.
    def LoadParameters(self):
        self.CONNECTION_INFO = {}
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')

    @QtCore.pyqtSlot()
    def SetConfiguration(self):
        self.dialogTextBrowser.exec_()

    def openInterface(self):
        if str(self.LabelConnection.currentText()) == 'udp':
            self.threads.runUDPThreadReceive()
            self.threads.runUDPThreadSend()
            self.connection = 'udp'
            self.LabelConnection.setEnabled(False)
            self.stopInterfaceButton.setEnabled(True)
        elif str(self.LabelConnection.currentText()) == 'serial':
            self.threads.runKISSThreadReceive()
            self.connection = 'serial'
            self.LabelConnection.setEnabled(False)
            self.stopInterfaceButton.setEnabled(True)

    def stopInterface(self):
        if self.connection == 'udp':
            self.threads.stopUDPThreadReceive()
            self.LabelConnection.setEnabled(True)
            self.stopInterfaceButton.setEnabled(False)
        elif self.connection == 'serial':
            self.threads.stopKISSThread()
            self.LabelConnection.setEnabled(True)
            self.stopInterfaceButton.setEnabled(False)

    def usage(self):
        log.msg("USAGE of client_amp.py")
        log.msg("")
        log.msg("python client_amp.py")
        log.msg("       [-n <username>] # Set SATNET username to login")
        log.msg("       [-p <password>] # Set SATNET user password to login")
        log.msg("       [-c <connection>] # Set the type of interface with "
                "the GS (serial, udp or tcp)")
        log.msg("       [-s <serialport>] # Set serial port")
        log.msg("       [-b <baudrate>] # Set serial port baudrate")
        log.msg("       [-i <ip>] # Set ip direction")
        log.msg("       [-u <udpport>] # Set port address")
        log.msg("")
        log.msg("Example for serial config:")
        log.msg("python client_amp.py -g -n crespo -p cre.spo -t 2 -c serial"
                "-s /dev/ttyS1 -b 115200")
        log.msg("Example for udp config:")
        log.msg("python client_amp.py -g -n crespo -p cre.spo -t 2 -c udp -i"
                "127.0.0.1 -u 5001")
        log.msg("")
        log.msg("[User]")
        log.msg("username: test-sc-user")
        log.msg("password: password")
        log.msg("connection: udp")
        log.msg("[Serial]")
        log.msg("serialport: /dev/ttyUSB0")
        log.msg("baudrate: 500000")
        log.msg("[UDP]")
        log.msg("ip: 127.0.0.1")
        log.msg("udpport: 5005")

    def center(self):
        frameGm = self.frameGeometry()
        screen_pos = QtGui.QApplication.desktop().cursor().pos()
        screen = QtGui.QApplication.desktop().screenNumber(screen_pos)
        centerPoint = QtGui.QApplication.desktop().screenGeometry(
            screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    # Functions designed to output information
    @QtCore.pyqtSlot(str)
    def append_text(self, text):
        self.console.moveCursor(QtGui.QTextCursor.End)
        self.console.insertPlainText(text)

        filename = ("log-" + self.CONNECTION_INFO['name'] +
                    "-" + time.strftime("%Y.%m.%d") + ".csv")
        with open(filename, "a+") as f:
            f.write(text)

    def closeEvent(self, event):
        self.reply = QtGui.QMessageBox.question(self, 'Exit confirmation',
                                                "Are you sure to quit?",
                                                QtGui.QMessageBox.Yes |
                                                QtGui.QMessageBox.No,
                                                QtGui.QMessageBox.No)

        # Non asynchronous way. Need to re implement this. TO-DO
        if self.reply == QtGui.QMessageBox.Yes:
            self.gsi.clear_slots()
            client_amp.Client(self.CONNECTION_INFO, self.gsi, self.threads).destroyconnection()
        elif self.reply == QtGui.QMessageBox.No:
            event.ignore()