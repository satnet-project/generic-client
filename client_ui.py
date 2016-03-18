# coding=utf-8
import os
from os import getcwd
import time
import logging

from PySide import QtGui, QtCore

# FIXME import sentence no optimized
import client_amp
from gs_interface import GroundStationInterface
from threads import Threads
from configurationWindow import ConfigurationWindow
from misc import set_data_local_file, get_data_local_file


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


# TODO Create a log configuration file.
class SatNetUI(QtGui.QWidget):
    def __init__(self, argumentsdict, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setFont(QtGui.QFont('Verdana', 11))
        self.enviromentDesktop = os.environ.get('DESKTOP_SESSION')

        self.connection = ''
        self.checkarguments(argumentsdict)

        self.UpdateFields()

        self.initUI()
        self.initButtons()
        self.initFields()
        self.setParameters()
        self.initLogo()
        self.initConfiguration()
        self.initConsole()

        self.dialogTextBrowser = ConfigurationWindow(self.settingsfile)

        self.gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo",
                                          client_amp.ClientProtocol)

        self.threads = Threads(self.CONNECTION_INFO, self.gsi)

        # Initialize the reactor parameters needed for the pyqt enviroment
        client_amp.Client(self.CONNECTION_INFO, self.gsi,
                          self.threads).createconnection(test=False)

        self.setWindowIcon(QtGui.QIcon('icon.png'))


    def NewConnection(self, test=False):
        """ New connection method.
        Create a new connection by loading the connection parameters
        from the interface window

        @param test: Useful flag for switch off reactor installation.
        @return: A call to the setconnection method.
        """
        self.CONNECTION_INFO['username'] = str(self.LabelUsername.text())
        self.CONNECTION_INFO['password'] = str(self.LabelPassword.text())
        self.CONNECTION_INFO['connection'] =\
            str(self.LabelConnection.currentText())

        if self.AutomaticReconnection.isChecked():
            self.CONNECTION_INFO['reconnection'] = 'yes'
        else:
            self.CONNECTION_INFO['reconnection'] = 'no'

        set_data_local_file(self.settingsfile, self.CONNECTION_INFO)

        if self.connection == '':
            self.openInterface()


        return client_amp.Client(self.CONNECTION_INFO, self.gsi,
                                 self.threads).setconnection(test,
                                                             self.settingsfile)

    def initUI(self):
        """ Init user interface method.
        Sets the initial parameters for the user interface main window.

        @return: None
        """
        self.CONNECTION_INFO = get_data_local_file(self.settingsfile)

        self.setFixedSize(1300, 800)
        self.setWindowTitle("SatNet client - %s" %
                            (self.CONNECTION_INFO['institution']))

        if self.CONNECTION_INFO['parameters'] == 'yes':
            self.CONNECTION_INFO = {}
            self.UpdateFields()
        elif self.CONNECTION_INFO['parameters'] == 'no':
            pass
        else:
            logging.info("No parameters configuration found." +
                         " Using default parameter - Yes")

    def initButtons(self):
        """

        @return: None
        """
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
        self.ButtonLoad.setToolTip("Load parameters from settings file")
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

    def savefields(self):
        """ Save fields method.

        @return: None
        """
        if self.LoadDefaultSettings.isChecked():
            self.CONNECTION_INFO['parameters'] = 'yes'
        elif not self.LoadDefaultSettings.isChecked():
            self.CONNECTION_INFO['parameters'] = 'no'

        if self.AutomaticReconnection.isChecked():
            self.CONNECTION_INFO['reconnection'] = 'yes'
        elif not self.AutomaticReconnection.isChecked():
            self.CONNECTION_INFO['reconnection'] = 'no'

        set_data_local_file(self.settingsfile, self.CONNECTION_INFO)

    def initFields(self):
        """

        @return: None.
        """
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

        configuration = QtGui.QGroupBox(self)
        configurationLayout = QtGui.QVBoxLayout()
        configuration.setLayout(configurationLayout)

        self.LoadDefaultSettings =\
            QtGui.QCheckBox("Automatically load settings from file")
        self.LoadDefaultSettings.stateChanged.connect(self.savefields)
        configurationLayout.addWidget(self.LoadDefaultSettings)
        self.AutomaticReconnection =\
            QtGui.QCheckBox("Reconnect after a failure")
        self.AutomaticReconnection.stateChanged.connect(self.savefields)
        configurationLayout.addWidget(self.AutomaticReconnection)

        configuration.move(10, 180)

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
        """ Init logo method.
        Place the log in its position.

        @return: None
        """
        LabelLogo = QtGui.QLabel(self)
        LabelLogo.move(20, 450)

        pic = QtGui.QPixmap(os.getcwd() + "/logo.png")

        LabelLogo.setPixmap(pic)
        LabelLogo.show()

    def initConfiguration(self):
        """

        @return: None
        """
        if self.CONNECTION_INFO['reconnection'] == 'yes':
            self.AutomaticReconnection.setChecked(True)
        elif self.CONNECTION_INFO['reconnection'] == 'no':
            self.AutomaticReconnection.setChecked(False)
        if self.CONNECTION_INFO['parameters'] == 'yes':
            self.LoadDefaultSettings.setChecked(True)
        elif self.CONNECTION_INFO['parameters'] == 'no':
            self.LoadDefaultSettings.setChecked(False)

    def initConsole(self):
        """

        @return: None.
        """
        self.console = QtGui.QTextBrowser(self)
        self.console.move(340, 10)
        self.console.resize(950, 780)
        self.console.setFont(QtGui.QFont('Helvetica', 12))

    # FIXME If some information are passed by terminal arguments this script
    # FIXME tries to draw it but the UI aren't build yet.
    def checkarguments(self, argumentsdict):
        """ Set arguments method.
        Check the arguments given in the argumentsdict. According these
        registers takes differents choices.

        @param argumentsdict:
        @return:
        """

        try:
            if argumentsdict['username'] != "":
                self.settingsfile= '.settings'
                set_data_local_file('.settings', argumentsdict)
                self.UpdateFields()
                logging.info("Arguments given by terminal.")
            if argumentsdict['username'] == '':
                self.settingsfile = '.settings'
                logging.info("No arguments given by terminal, using "
                             "configuration file.")
        except KeyError:
            self.settingsfile =  argumentsdict['file']

    # Set parameters from CONNECTION_INFO dict.
    # TODO Merge!
    def setParameters(self):
        self.UpdateFields()
        self.FieldLabelAttemps.setText(self.CONNECTION_INFO['attempts'])
        self.LabelUsername.setText(self.CONNECTION_INFO['username'])

        try:
            index = self.LabelConnection.findText(
                self.CONNECTION_INFO['connection'])
            self.LabelConnection.setCurrentIndex(index)
        except Exception as e:
            logging.error(e)

    def CloseConnection(self):
        """ Close connection method

        @return: None
        """
        if self.gsi.clear_slots():
            self.ButtonNew.setEnabled(True)
            self.ButtonCancel.setEnabled(False)

    def UpdateFields(self):
        """

        @return:
        """
        self.CONNECTION_INFO = get_data_local_file(self.settingsfile)

        settingsfile = str(getcwd()) + '/' + str(self.settingsfile)
        logging.info("Parameters loaded from %s." %(settingsfile))


    @QtCore.Slot()
    def SetConfiguration(self):
        """

        @return:
        """
        self.dialogTextBrowser.exec_()
        self.UpdateFields()

    # TODO Check connection is established before changing buttons state
    def openInterface(self):
        """

        @return:
        """
        if str(self.LabelConnection.currentText()) == 'udp':
            self.threads.runUDPThreadReceive()
            self.threads.runUDPThreadSend()
            self.connection = 'udp'
            self.LabelConnection.setEnabled(False)
            self.stopInterfaceButton.setEnabled(True)
        elif str(self.LabelConnection.currentText()) == 'tcp':
            self.threads.runTCPThreadReceive()
            self.threads.runTCPThreadSend()
            self.connection = 'tcp'
            self.LabelConnection.setEnabled(False)
            self.stopInterfaceButton.setEnabled(True)
        elif str(self.LabelConnection.currentText()) == 'serial':
            if self.threads.runKISSThreadReceive():
                self.connection = 'serial'
                self.LabelConnection.setEnabled(False)
                self.stopInterfaceButton.setEnabled(True)

    # TODO Check connection is gone before disabling button
    def stopInterface(self):
        """

        @return:
        """
        if self.connection == 'udp':
            if self.threads.stopUDPThreadReceive():
                self.LabelConnection.setEnabled(True)
                self.stopInterfaceButton.setEnabled(False)
        if self.connection == 'tcp':
            self.threads.stopUDPThreadReceive()
            self.LabelConnection.setEnabled(True)
            self.stopInterfaceButton.setEnabled(False)
        elif self.connection == 'serial':
            self.threads.stopKISSThread()
            self.LabelConnection.setEnabled(True)
            self.stopInterfaceButton.setEnabled(False)

    def usage(self):
        """ Emits a useful message.
        Emits a useful message involved in program configuration.

        @return: None.
        """
        logging.info("USAGE of client_amp.py")
        logging.info("")
        logging.info("python client_amp.py")
        logging.info("       [-n <username>] # Set SATNET username to login")
        logging.info("       [-p <password>] # Set SATNET user password "
                     "to login")
        logging.info("       [-c <connection>] # Set the type of interface "
                     "with the GS (serial, udp or tcp)")
        logging.info("       [-s <serialport>] # Set serial port")
        logging.info("       [-b <baudrate>] # Set serial port baudrate")
        logging.info("       [-i <ip>] # Set ip direction")
        logging.info("       [-u <udpport>] # Set port address")
        logging.info("")
        logging.info("Example for serial config:")
        logging.info("python client_amp.py -g -n crespo -p cre.spo -t 2 "
                    "-c serial -s /dev/ttyS1 -b 115200")
        logging.info("Example for udp config:")
        logging.info("python client_amp.py -g -n crespo -p cre.spo -t 2 -c "
                    "udp -i 127.0.0.1 -u 5001")
        logging.info("")
        logging.info("[User]")
        logging.info("username: test-sc-user")
        logging.info("password: password")
        logging.info("connection: udp")
        logging.info("[Serial]")
        logging.info("serialport: /dev/ttyUSB0")
        logging.info("baudrate: 500000")
        logging.info("[UDP]")
        logging.info("ip: 127.0.0.1")
        logging.info("udpport: 5005")

    def center(self):
        """ Center window method.
        Puts the main window in the center of the screen.

        @return: None.
        """
        frameGm = self.frameGeometry()
        screen_pos = QtGui.QApplication.desktop().cursor().pos()
        screen = QtGui.QApplication.desktop().screenNumber(screen_pos)
        centerPoint = QtGui.QApplication.desktop().screenGeometry(
            screen).center()
        frameGm.moveCenter(centerPoint)
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    @QtCore.Slot(str)
    def append_text(self, text):
        """

        @param text:
        @return:
        """
        self.console.moveCursor(QtGui.QTextCursor.End)
        self.console.insertPlainText(text)

        if "Connection lost" in str(text):
            self.ButtonNew.setEnabled(True)
            self.ButtonCancel.setEnabled(False)

        if "Connection failed" in str(text):
            self.ButtonNew.setEnabled(True)
            self.ButtonCancel.setEnabled(False)

        if "Connection sucessful" in str(text):
            self.ButtonNew.setEnabled(False)
            self.ButtonCancel.setEnabled(True)

        filename = ("log-" + self.CONNECTION_INFO['institution'] +
                    "-" + time.strftime("%Y.%m.%d") + ".csv")
        with open(filename, "a+") as f:
            f.write(text)


    def sigint_handler(self, *args):
        """
        import  sys
        sys.stderr.write('\r')
        # self.closeEvent()
        """
        logging.info("adios!")

    def closeEvent(self, event):
        """

        @param event:
        @return:
        """
        self.reply = QtGui.QMessageBox.question(self, 'Exit confirmation',
                                                "Are you sure to quit?",
                                                QtGui.QMessageBox.Yes |
                                                QtGui.QMessageBox.No,
                                                QtGui.QMessageBox.No)

        # TODO Non asynchronous way. Need to re implement this.
        if self.reply == QtGui.QMessageBox.Yes:
            self.stopInterface()
            self.gsi.clear_slots()
            client_amp.Client(self.CONNECTION_INFO, self.gsi, self.threads).destroyconnection()
        elif self.reply == QtGui.QMessageBox.No:
            event.ignore()