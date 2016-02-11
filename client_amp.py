# coding=utf-8
import sys
import os
import misc
import warnings
import ConfigParser
import time

from PyQt4 import QtGui, QtCore

from Queue import Queue
from OpenSSL import SSL

from twisted.python import log
from twisted.internet import ssl

from twisted.internet.ssl import ClientContextFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.amp import AMP
from twisted.internet.defer import inlineCallbacks

from ampCommands import Login, StartRemote, NotifyMsg
from ampCommands import NotifyEvent, SendMsg, EndRemote

from gs_interface import GroundStationInterface, OperativeUDPThreadReceive
from gs_interface import OperativeUDPThreadSend
from gs_interface import OperativeTCPThread, OperativeKISSThread


"""
   Copyright 2015, 2016 Samuel Góngora García
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


class ClientProtocol(AMP):
    """
    Client class
    """

    def __init__(self, CONNECTION_INFO, gsi, threads):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi
        self.threads = threads
        self.initThreads()

    def initThreads(self):
        if self.CONNECTION_INFO['connection'] == 'udp':
            self.threads.runUDPThreadReceive()
            self.threads.runUDPThreadSend()
        elif self.CONNECTION_INFO['connection'] == 'serial':
            self.threads.runKISSThreadReceive()

    def connectionMade(self):
        self.user_login()
        self.gsi.connectProtocol(self)

    def connectionLost(self, reason):
        log.msg("Connection lost")

        """
        If the connection with the twisted server is lost disconnects all
        active GroundStation connections
        """
        if self.CONNECTION_INFO['connection'] == 'udp':
            self.threads.stopUDPThreadReceive()
        elif self.CONNECTION_INFO['connection'] == 'tcp':
            pass
        elif self.CONNECTION_INFO['connection'] == 'serial':
            self.threads.stopKISSThread()
        elif self.CONNECTION_INFO['connection'] == 'none':
            pass

    def connectionFailed(self, reason):
        log.msg("Connection failed")

    @inlineCallbacks
    def end_connection(self):
        res = yield self.callRemote(EndRemote)
        log.msg(res)

    @inlineCallbacks
    def user_login(self):
        res = yield self.callRemote(Login,
                                    sUsername=self.CONNECTION_INFO['username'],
                                    sPassword=self.CONNECTION_INFO['password'])

        if res['bAuthenticated'] is True:
            res = yield self.callRemote(StartRemote,
                                        iSlotId=self.CONNECTION_INFO['slot_id']
                                        )
        elif res['bAuthenticated'] is False:
            log.msg('False')
        else:
            log.msg('No data')

    # To-do. Do we need a return connection?
    def vNotifyMsg(self, sMsg):
        log.msg("(" + self.CONNECTION_INFO['username'] +
                ") --------- Notify Message ---------")

        if self.CONNECTION_INFO['connection'] == 'serial':
            log.msg(sMsg)

            import kiss
            self.kissTNC = kiss.KISS(self.CONNECTION_INFO['serialport'],
                                     self.CONNECTION_INFO['baudrate'])
            self.kissTNC.start()
            self.kissTNC.write(sMsg)

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'udp':
            log.msg(sMsg)
            self.threads.UDPThreadSend(sMsg)

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'tcp':
            log.msg(sMsg)

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'none':
            log.msg(sMsg)
            """
            Save to local file
            """
            log.msg('---- Message saved to local file ----')
            filename = ("ESEO-RECEIVEDFRAMES-" + self.CONNECTION_INFO['name'] +
                        "-" + time.strftime("%Y.%m.%d") + ".csv")
            with open(filename, "a+") as f:
                f.write(sMsg + ",\n")

            return {'bResult': True}

    NotifyMsg.responder(vNotifyMsg)

    # Method associated to frame processing.
    def _processframe(self, frame):
        frameProcessed = []
        frameProcessed = list(frame)
        frameProcessed = ":".join("{:02x}".format(ord(c))
                                  for c in frameProcessed)

        log.msg("Received frame: ", frameProcessed)

        self.processFrame(frameProcessed)

    @inlineCallbacks
    def processFrame(self, frameProcessed):
        try:
            yield self.callRemote(SendMsg, sMsg=frameProcessed,
                                  iTimestamp=misc.get_utc_timestamp())
        except Exception as e:
            log.err(e)
            log.err("Error")

    def vNotifyEvent(self, iEvent, sDetails):
        log.msg("(" + self.CONNECTION_INFO['username'] +
                ") --------- Notify Event ---------")
        if iEvent == NotifyEvent.SLOT_END:
            log.msg("Disconnection because the slot has ended")
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.REMOTE_DISCONNECTED:
            log.msg("Remote client has lost the connection")
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.END_REMOTE:
            log.msg("The remote client has closed the connection")
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.REMOTE_CONNECTED:
            log.msg("The remote client has just connected")

        return {}
    NotifyEvent.responder(vNotifyEvent)


class Threads(object):

    def __init__(self, CONNECTION_INFO, gsi):
        self.UDPSignal = True
        self.serialSignal = True
        self.TCPSignal = True
        self.tcp_queue = Queue()
        self.udp_queue = Queue()
        self.serial_queue = Queue()
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi

    def runUDPThreadReceive(self):
        self.workerUDPThreadReceive = OperativeUDPThreadReceive(self.udp_queue,
                                                                self.sendData,
                                                                self.UDPSignal,
                                                                self.CONNECTION_INFO)
        self.workerUDPThreadReceive.start()

    def stopUDPThreadReceive(self):
        self.workerUDPThreadReceive.stop()

    def runUDPThreadSend(self):
        self.workerUDPThreadSend = OperativeUDPThreadSend(self.CONNECTION_INFO)

    def UDPThreadSend(self, message):
        self.workerUDPThreadSend.send(message)

    def runKISSThreadReceive(self):
        self.workerKISSThread = OperativeKISSThread(self.serial_queue,
                                                    self.sendData,
                                                    self.serialSignal,
                                                    self.CONNECTION_INFO)
        self.workerKISSThread.start()

    def stopKISSThread(self):
        self.workerKISSThread.stop()

    # To-do
    def runTCPThread(self):
        self.workerTCPThread = OperativeTCPThread(self.tcp_queue,
                                                  self.sendData,
                                                  self.TCPSignal,
                                                  self.CONNECTION_INFO)
        self.workerTCPThread.start()

    # Stop TCP thread
    def stopTCPThread(self):
        self.workerTCPThread.stop()

    def sendData(self, result):
        log.msg(result)
        self.gsi._manageFrame(result)


class ClientReconnectFactory(ReconnectingClientFactory):
    """
    ReconnectingClientFactory inherited object class to handle
    the reconnection process.
    """
    def __init__(self, CONNECTION_INFO, gsi, threads):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi
        self.threads = threads

    # Called when a connection has been started
    def startedConnecting(self, connector):
        log.msg("Starting connection............................" +
                "..............................................." +
                ".........................................")

    # Create an instance of a subclass of Protocol
    def buildProtocol(self, addr):
        log.msg("Building protocol.............................." +
                "..............................................." +
                ".........................")
        self.resetDelay()
        return ClientProtocol(self.CONNECTION_INFO, self.gsi,
                              self.threads)

    # Called when an established connection is lost
    def clientConnectionLost(self, connector, reason):
        if self.CONNECTION_INFO['reconnection'] == 'yes':
            self.continueTrying = True
        elif self.CONNECTION_INFO['reconnection'] == 'no':
            self.continueTrying = None

        log.msg('Lost connection. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionLost(self,
                                                       connector,
                                                       reason)

    # Called when a connection has failed to connect
    def clientConnectionFailed(self, connector, reason):
        if self.CONNECTION_INFO['reconnection'] == 'yes':
            self.continueTrying = True
        elif self.CONNECTION_INFO['reconnection'] == 'no':
            self.continueTrying = None

        log.msg('Connection failed. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionFailed(self,
                                                         connector,
                                                         reason)


class CtxFactory(ClientContextFactory):

    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)

        return ctx


class Client(object):
    """
    This class starts the client using the data provided by user interface.
    :ivar CONNECTION_INFO:
        This variable contains the following data: username, password,
        slot_id, connection (either 'serial' or 'udp'), serialport,
        baudrate, ip, port.
    :type CONNECTION_INFO:
        L{Dictionary}
    :ivar
    """
    def __init__(self, CONNECTION_INFO):
        self.CONNECTION_INFO = CONNECTION_INFO

    def createConnection(self):
        gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo",
                                     ClientProtocol)
        threads = Threads(self.CONNECTION_INFO, gsi)

        global connector
        connector = reactor.connectSSL(str(self.CONNECTION_INFO['serverip']),
                                       int(self.CONNECTION_INFO['serverport']),
                                       ClientReconnectFactory(
                                        self.CONNECTION_INFO,
                                        gsi, threads),
                                       CtxFactory())

        return gsi, connector


# QDialog, QWidget or QMainWindow, which is better in this situation? TO-DO
class SATNetGUI(QtGui.QWidget):
    def __init__(self, argumentsDict, parent=None):
        QtGui.QWidget.__init__(self, parent)
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 18))

        self.enviromentDesktop = os.environ.get('DESKTOP_SESSION')

        self.initUI()
        self.initButtons()
        self.initFields()
        self.setParameters()
        self.initLogo()
        self.initConfiguration()
        self.initConsole()

        #  Use a dict for passing arg.
        self.setArguments(argumentsDict)

    # Create a new connection by loading the connection parameters
    # from the interface window
    def NewConnection(self):
        self.CONNECTION_INFO['username'] = str(self.LabelUsername.text())
        self.CONNECTION_INFO['password'] = str(self.LabelPassword.text())
        self.CONNECTION_INFO['slot_id'] = int(self.LabelSlotID.text())
        self.CONNECTION_INFO['connection'] =\
            str(self.LabelConnection.currentText())

        if self.CONNECTION_INFO['connection'] == 'serial':
            self.CONNECTION_INFO['serialport'] =\
             str(self.LabelSerialPort.currentText())
            self.CONNECTION_INFO['baudrate'] = str(self.LabelBaudrate.text())
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.CONNECTION_INFO['udpipsend'] = self.LabelIP.text()
            self.CONNECTION_INFO['udpportsend'] = int(
                self.LabelIPPort.text())
        elif self.CONNECTION_INFO['connection'] == 'tcp':
            self.CONNECTION_INFO['tcpip'] = self.LabelIP.text()
            self.CONNECTION_INFO['tcpport'] = int(self.LabelIPPort.text())
        elif self.CONNECTION_INFO['connection'] == 'none':
            log.msg('No GS connection. The client will just listen.')
            self.CONNECTION_INFO['serverip'] = self.LabelIP.text()
            self.CONNECTION_INFO['serverport'] = int(self.LabelIPPort.text())
        else:
            print "error"

        self.gsi, self.c = Client(self.CONNECTION_INFO).createConnection()

        # Start the selected connection
        if self.CONNECTION_INFO['connection'] == 'tcp':
            self.runTCPThread()
        elif self.CONNECTION_INFO['connection'] == 'none':
            pass
        else:
            pass

        self.ButtonNew.setEnabled(False)
        self.ButtonCancel.setEnabled(True)
        self.LoadDefaultSettings.setEnabled(False)
        self.AutomaticReconnection.setEnabled(False)

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
            warnings.warn("No parameters configuration found." +
                          " Using default parameter - Yes")

    def initButtons(self):
        # Control buttons.
        buttons = QtGui.QGroupBox(self)
        grid = QtGui.QGridLayout(buttons)
        buttons.setLayout(grid)

        # New connection.
        self.ButtonNew = QtGui.QPushButton("Connection")
        self.ButtonNew.setToolTip("Start a new connection using " +
                                  " the selected connection")
        self.ButtonNew.setFixedWidth(145)
        self.ButtonNew.clicked.connect(self.NewConnection)
        # Close connection.
        self.ButtonCancel = QtGui.QPushButton("Disconnection")
        self.ButtonCancel.setToolTip("End current connection")
        self.ButtonCancel.setFixedWidth(145)
        self.ButtonCancel.clicked.connect(self.CloseConnection)
        self.ButtonCancel.setEnabled(False)
        # Load parameters from file
        ButtonLoad = QtGui.QPushButton("Load parameters from file")
        ButtonLoad.setToolTip("Load parameters from <i>.settings</i> file")
        ButtonLoad.setFixedWidth(296)
        ButtonLoad.clicked.connect(self.UpdateFields)
        # Configuration
        ButtonConfiguration = QtGui.QPushButton("Configuration")
        ButtonConfiguration.setToolTip("Open configuration window")
        ButtonConfiguration.setFixedWidth(145)
        ButtonConfiguration.clicked.connect(self.SetConfiguration)
        # Help.
        ButtonHelp = QtGui.QPushButton("Help")
        ButtonHelp.setToolTip("Click for help")
        ButtonHelp.setFixedWidth(145)
        ButtonHelp.clicked.connect(self.usage)
        grid.addWidget(self.ButtonNew, 0, 0, 1, 1)
        grid.addWidget(self.ButtonCancel, 0, 1, 1, 1)
        grid.addWidget(ButtonLoad, 1, 0, 1, 2)
        grid.addWidget(ButtonConfiguration, 2, 0, 1, 1)
        grid.addWidget(ButtonHelp, 2, 1, 1, 1)
        buttons.setTitle("Connection")
        buttons.move(10, 10)

        self.dialogTextBrowser = ConfigurationWindow(self)

    def initFields(self):
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
        self.LabelSlotID = QtGui.QLineEdit()
        self.LabelSlotID.setFixedWidth(190)
        self.layout.addRow(QtGui.QLabel("slot_id:        "),
                           self.LabelSlotID)

        self.LabelConnection = QtGui.QComboBox()
        self.LabelConnection.setFixedWidth(190)
        self.LabelConnection.addItems(['serial', 'udp', 'tcp', 'none'])
        self.LabelConnection.activated.connect(self.CheckConnection)
        self.layout.addRow(QtGui.QLabel("Connection:     "),
                           self.LabelConnection)

        parameters.setTitle("User data")
        parameters.move(10, 145)

        """
        Create a new 'set' of labels for connection parameters
        """
        if self.enviromentDesktop == 'lightdm-xsession':
            #  Mate desktop
            self.LabelSerialPort = QtGui.QComboBox()
            from glob import glob
            ports = glob('/dev/tty[A-Za-z]*')
            self.LabelSerialPort.addItems(ports)
            self.layout.addRow(QtGui.QLabel("Serial port:  "),
                               self.LabelSerialPort)
            self.LabelBaudrate = QtGui.QLineEdit()
            self.layout.addRow(QtGui.QLabel("Baudrate:     "),
                               self.LabelBaudrate)
            self.LabelIP = QtGui.QLineEdit()
            self.layout.addRow(QtGui.QLabel("SATNet host:  "),
                               self.LabelIP)
            self.LabelIPPort = QtGui.QLineEdit()
            self.layout.addRow(QtGui.QLabel("Port:         "),
                               self.LabelIPPort)
        else:
            if self.CONNECTION_INFO['connection'] == 'serial':
                self.LabelSerialPort = QtGui.QComboBox()
                self.LabelSerialPort.setFixedWidth(190)
                from glob import glob
                ports = glob('/dev/tty[A-Za-z]*')
                self.LabelSerialPort.addItems(ports)
                self.layout.addRow(QtGui.QLabel("Serial port:  "),
                                   self.LabelSerialPort)
                self.LabelBaudrate = QtGui.QLineEdit()
                self.LabelBaudrate.setFixedWidth(190)
                self.layout.addRow(QtGui.QLabel("Baudrate:     "),
                                   self.LabelBaudrate)
            elif self.CONNECTION_INFO['connection'] == 'udp':
                self.LabelIP = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Remote:       "),
                                   self.LabelIP)
                self.LabelIPPort = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Port:         "),
                                   self.LabelIPPort)
            elif self.CONNECTION_INFO['connection'] == 'tcp':
                self.LabelIP = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Remote TCP:   "),
                                   self.LabelIP)
                self.LabelIPPort = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Port:         "),
                                   self.LabelIPPort)
            elif self.CONNECTION_INFO['connection'] == 'none':
                self.LabelIP = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("SatNet host:  "),
                                   self.LabelIP)
                self.LabelIPPort = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Port:         "),
                                   self.LabelIPPort)
            else:
                log.msg("Error opening a connection interface")

        # Configuration group.
        configuration = QtGui.QGroupBox(self)
        configurationLayout = QtGui.QVBoxLayout()
        configuration.setLayout(configurationLayout)

        self.LoadDefaultSettings =\
            QtGui.QCheckBox("Automatically load settings from '.settings'")
        configurationLayout.addWidget(self.LoadDefaultSettings)
        self.AutomaticReconnection =\
            QtGui.QCheckBox("Reconnect after a failure")
        configurationLayout.addWidget(self.AutomaticReconnection)

        # configuration.setTitle("Basic configuration")
        configuration.move(10, 380)

    def initLogo(self):
        LabelLogo = QtGui.QLabel(self)
        LabelLogo.move(40, 490)
        pic = QtGui.QPixmap(os.getcwd() + "/logo.png")
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
    def setArguments(self, argumentsDict):
        if argumentsDict['username'] != "":
            self.LabelUsername.setText(argumentsDict['username'])
        if argumentsDict['password'] != "":
            self.LabelPassword.setText(argumentsDict['password'])
        if argumentsDict['slot'] != "":
            self.LabelSlotID.setText(argumentsDict['slot'])
        if argumentsDict['connection'] != "":
            index = self.LabelConnection.findText(argumentsDict['connection'])
            self.LabelConnection.setCurrentIndex(index)
        if argumentsDict['serialport'] != "":
            index = self.LabelSerialPort.findText(argumentsDict['serialport'])
            self.LabelSerialPort.setCurrentIndex(index)
        if argumentsDict['baudrate'] != "":
            self.LabelBaudrate.setText(argumentsDict['baudrate'])
        if argumentsDict['udpipsend'] != "":
            self.LabelIP.setText(argumentsDict['udpipsend'])
        if argumentsDict['udpportsend'] != "":
            self.LabelIPPort.setText(argumentsDict['udpportsend'])

    # Set parameters from CONNECTION_INFO dict.
    def setParameters(self):
        self.LabelUsername.setText(self.CONNECTION_INFO['username'])
        self.LabelPassword.setText(self.CONNECTION_INFO['password'])
        self.LabelSlotID.setText(self.CONNECTION_INFO['slot_id'])

        try:
            index = self.LabelConnection.findText(
                self.CONNECTION_INFO['connection'])
            self.LabelConnection.setCurrentIndex(index)
        except Exception as e:
            log.err(e)

        #  To-do. Optimized!
        if self.CONNECTION_INFO['connection'] == 'serial':
            index = self.LabelSerialPort.findText(
                self.CONNECTION_INFO['serialport'])
            self.LabelSerialPort.setCurrentIndex(index)
            self.LabelBaudrate.setText(self.CONNECTION_INFO['baudrate'])
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.LabelIP.setText(self.CONNECTION_INFO['udpipsend'])
            self.LabelIPPort.setText(self.CONNECTION_INFO['udpportsend'])
        elif self.CONNECTION_INFO['connection'] == 'tcp':
            self.LabelIP.setText(self.CONNECTION_INFO['tcpip'])
            self.LabelIPPort.setText(self.CONNECTION_INFO['ipport'])
        elif self.CONNECTION_INFO['connection'] == 'none':
            self.LabelIP.setText(self.CONNECTION_INFO['serverip'])
            self.LabelIPPort.setText(str(self.CONNECTION_INFO['serverport']))
        else:
            raise Exception

    def CloseConnection(self):
        try:
            self.gsi.clear_slots()
        except:
            pass

        self.ButtonNew.setEnabled(True)
        self.ButtonCancel.setEnabled(False)

    def UpdateFields(self):
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')

        #  To-do. Improve try-except with errors catching.
        self.LabelUsername.setText(self.CONNECTION_INFO['username'])
        self.LabelPassword.setText(self.CONNECTION_INFO['password'])
        self.LabelSlotID.setText(self.CONNECTION_INFO['slot_id'])
        try:
            index = self.LabelConnection.findText(
                self.CONNECTION_INFO['connection'])
            self.LabelConnection.setCurrentIndex(index)
        except Exception as e:
            log.err(e)

        #  To-do. Optimized!
        if self.CONNECTION_INFO['connection'] == 'serial':
            index = self.LabelSerialPort.findText(
                self.CONNECTION_INFO['serialport'])
            self.LabelSerialPort.setCurrentIndex(index)
            self.LabelBaudrate.setText(self.CONNECTION_INFO['baudRate'])
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.LabelIP.setText(self.CONNECTION_INFO['udpipsend'])
            self.LabelIPPort.setText(self.CONNECTION_INFO['udpportsend'])
        elif self.CONNECTION_INFO['connection'] == 'tcp':
            self.LabelIP.setText(self.CONNECTION_INFO['tcpip'])
            self.LabelIPPort.setText(self.CONNECTION_INFO['tcpport'])
        elif self.CONNECTION_INFO['connection'] == 'none':
            self.LabelIP.setText(self.CONNECTION_INFO['serverip'])
            self.LabelIPPort.setText(str(self.CONNECTION_INFO['serverport']))
        else:
            raise Exception

        log.msg("Parameters loaded from .setting file.")

    # Load connection parameters from .settings file.
    def LoadParameters(self):
        self.CONNECTION_INFO = {}
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')

    @QtCore.pyqtSlot()
    def SetConfiguration(self):
        self.dialogTextBrowser.exec_()

    def deleteMenu(self):
        try:
            SerialPort = self.layout.labelForField(self.LabelSerialPort)
            if SerialPort is not None:
                SerialPort.deleteLater()
            self.LabelSerialPort.deleteLater()

            BaudRate = self.layout.labelForField(self.LabelBaudrate)
            if BaudRate is not None:
                BaudRate.deleteLater()
            self.LabelBaudrate.deleteLater()
        except:
            pass
        try:
            LabelIP = self.layout.labelForField(self.LabelIP)
            if LabelIP is not None:
                LabelIP.deleteLater()
            self.LabelIP.deleteLater()

            LabelIPPort = self.layout.labelForField(self.LabelIPPort)
            if LabelIPPort is not None:
                LabelIPPort.deleteLater()
            self.LabelIPPort.deleteLater()
        except:
            pass

    def CheckConnection(self):
        self.LoadParameters()

        self.LabelUsername.setText(self.CONNECTION_INFO['username'])
        self.LabelPassword.setText(self.CONNECTION_INFO['password'])

        self.LabelSlotID.setFixedWidth(190)
        self.LabelConnection.setFixedWidth(190)

        if str(self.LabelConnection.currentText()) == 'serial':
            self.deleteMenu()

            self.LabelSerialPort = QtGui.QComboBox()
            self.LabelSerialPort.setFixedWidth(190)

            from glob import glob
            ports = glob('/dev/tty[A-Za-z]*')
            self.LabelSerialPort.addItems(ports)
            self.layout.addRow(QtGui.QLabel("Serial port:  "),
                               self.LabelSerialPort)
            self.LabelBaudrate = QtGui.QLineEdit()
            self.LabelBaudrate.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("Baudrate:     "),
                               self.LabelBaudrate)

            index = self.LabelSerialPort.findText(
                self.CONNECTION_INFO['serialport'])
            self.LabelSerialPort.setCurrentIndex(index)
            self.LabelBaudrate.setText(self.CONNECTION_INFO['baudrate'])

        elif str(self.LabelConnection.currentText()) == 'udp':
            self.deleteMenu()

            self.LabelIP = QtGui.QLineEdit()
            self.LabelIP.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("UDP remote:   "), self.LabelIP)
            self.LabelIPPort = QtGui.QLineEdit()
            self.LabelIPPort.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("Port:         "),
                               self.LabelIPPort)

            # Gets data from .settings file not from user interface
            # To-do
            self.LabelIP.setText(self.CONNECTION_INFO['udpipsend'])
            self.LabelIPPort.setText(str(
                self.CONNECTION_INFO['udpportsend']))

        elif str(self.LabelConnection.currentText()) == 'tcp':
            self.deleteMenu()

            self.LabelIP = QtGui.QLineEdit()
            self.LabelIP.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("TCP remote:   "), self.LabelIP)
            self.LabelIPPort = QtGui.QLineEdit()
            self.LabelIPPort.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("Port:         "),
                               self.LabelIPPort)

            # Gets data from .settings file not from user interface
            # To-do
            self.LabelIP.setText(self.CONNECTION_INFO['tcpip'])
            self.LabelIPPort.setText(str(self.CONNECTION_INFO['tcpport']))

        elif str(self.LabelConnection.currentText()) == 'none':
            self.deleteMenu()

            self.LabelIP = QtGui.QLineEdit()
            self.LabelIP.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("SatNet server:"),
                               self.LabelIP)
            self.LabelIPPort = QtGui.QLineEdit()
            self.LabelIPPort.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("Port:         "),
                               self.LabelIPPort)

            self.LabelIP.setText(self.CONNECTION_INFO['serverip'])
            self.LabelIPPort.setText(str(self.CONNECTION_INFO['serverport']))

    def usage(self):
        log.msg("USAGE of client_amp.py")
        log.msg("")
        log.msg("python client_amp.py")
        log.msg("       [-n <username>] # Set SATNET username to login")
        log.msg("       [-p <password>] # Set SATNET user password to login")
        log.msg("       [-t <slot_ID>] # Set the slot id corresponding to "
                "the pass you will track")
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
        log.msg("slot_id: -1")
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

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Exit confirmation',
                                           "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)

        # Non asynchronous way. Need to re implement this. TO-DO
        if reply == QtGui.QMessageBox.Yes:
            try:
                self.gsi.clear_slots()
            except AttributeError as e:
                log.err(e)
                log.err("Unable to stop a connection never created")

            try:
                reactor.stop()
                log.msg("Reactor stopped")
                event.accept()
            except Exception as e:
                log.err(e)
                log.err("Reactor not running")
                event.ignore()
        elif reply == QtGui.QMessageBox.No:
            event.ignore()


class ConfigurationWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ConfigurationWindow, self).__init__(parent)

        self.setWindowTitle("SatNet client - Advanced configuration")

        parameters = QtGui.QGroupBox(self)
        grid = QtGui.QGridLayout(parameters)
        parameters.setLayout(grid)

        LabelClientname = QtGui.QLabel("Client name:           ")
        self.FieldClientname = QtGui.QLineEdit()
        self.FieldClientname.setFixedWidth(200)
        LabelPassword = QtGui.QLabel("Reconnection attempts: ")
        self.FieldLabelPassword = QtGui.QLineEdit()
        self.FieldLabelPassword.setFixedWidth(200)
        LabelServer = QtGui.QLabel("Server address:        ")
        self.FieldLabelServer = QtGui.QLineEdit()
        self.FieldLabelServer.setFixedWidth(200)
        LabelPort = QtGui.QLabel("Server port:           ")
        self.FieldLabelPort = QtGui.QLineEdit()
        self.FieldLabelPort.setFixedWidth(200)
        LabelUDPIPSend = QtGui.QLabel("UDP remote IP:           ")
        self.FieldLabelUDPIpSend = QtGui.QLineEdit()
        self.FieldLabelUDPIpSend.setFixedWidth(200)
        LabelUPDPortSend = QtGui.QLabel("UDP remote port:         ")
        self.FieldLabelUDPPortSend = QtGui.QLineEdit()
        self.FieldLabelUDPPortSend.setFixedWidth(200)
        LabelUDPIPReceive = QtGui.QLabel("UDP local IP:            ")
        self.FieldLabelUDPIPReceive = QtGui.QLineEdit()
        self.FieldLabelUDPIPReceive.setFixedWidth(200)
        LabelUDPPortReceive = QtGui.QLabel("UDP local port:          ")
        self.FieldLabelUDPPortRececeive = QtGui.QLineEdit()
        self.FieldLabelUDPPortRececeive.setFixedWidth(200)

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close |
                                     QtGui.QDialogButtonBox.Save)

        buttonBox.button(QtGui.QDialogButtonBox.Close).clicked.connect(
            self.closeWindow)
        buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(
            self.save)

        grid.addWidget(LabelClientname, 0, 0, 1, 1)
        grid.addWidget(self.FieldClientname, 0, 1, 1, 1)
        grid.addWidget(LabelPassword, 1, 0, 1, 1)
        grid.addWidget(self.FieldLabelPassword, 1, 1, 1, 1)
        grid.addWidget(LabelServer, 2, 0, 1, 1)
        grid.addWidget(self.FieldLabelServer, 2, 1, 1, 1)
        grid.addWidget(LabelPort, 3, 0, 1, 1)
        grid.addWidget(self.FieldLabelPort, 3, 1, 1, 1)
        grid.addWidget(LabelUDPIPSend, 4, 0, 1, 1)
        grid.addWidget(self.FieldLabelUDPIpSend, 4, 1, 1, 1)
        grid.addWidget(LabelUPDPortSend, 5, 0, 1, 1)
        grid.addWidget(self.FieldLabelUDPPortSend, 5, 1, 1, 1)
        grid.addWidget(LabelUDPIPReceive, 6, 0, 1, 1)
        grid.addWidget(self.FieldLabelUDPIPReceive, 6, 1, 1, 1)
        grid.addWidget(LabelUDPPortReceive, 7, 0, 1, 1)
        grid.addWidget(self.FieldLabelUDPPortRececeive, 7, 1, 1, 1)
        grid.addWidget(buttonBox, 8, 0, 1, 2)

        import platform
        os = platform.linux_distribution()
        if os[0] == 'debian':
            self.setMinimumSize(410, 415)
        else:
            self.setMinimumSize(410, 335)
        parameters.setTitle("Connection")
        parameters.move(10, 10)

        # Read fields
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')
        self.FieldClientname.setText(
            self.CONNECTION_INFO['username'])
        self.FieldLabelPassword.setText(
            self.CONNECTION_INFO['password'])
        self.FieldLabelServer.setText(
            self.CONNECTION_INFO['serverip'])
        self.FieldLabelPort.setText(str(
            self.CONNECTION_INFO['serverport']))
        self.FieldLabelUDPIpSend.setText(
            self.CONNECTION_INFO['udpipsend'])
        self.FieldLabelUDPPortSend.setText(
            self.CONNECTION_INFO['udpportsend'])
        self.FieldLabelUDPIPReceive.setText(
            self.CONNECTION_INFO['udpipreceive'])
        self.FieldLabelUDPPortRececeive.setText(str(
            self.CONNECTION_INFO['udpportreceive']))

    def closeWindow(self):
        self.close()

    def save(self):
        config = ConfigParser.SafeConfigParser()
        config.read(".settings")

        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')

        name = self.FieldClientname.text()
        password = self.FieldLabelPassword.text()
        server = self.FieldLabelServer.text()
        port = self.FieldLabelPort.text()
        udpipsend = self.FieldLabelUDPIpSend.text()
        udpportsend = self.FieldLabelUDPPortSend.text()
        udpipreceive = self.FieldLabelUDPIPReceive.text()
        udpportreceive = self.FieldLabelUDPPortRececeive.text()

        if self.CONNECTION_INFO['username'] != name:
            config.set('User', 'username', str(name))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['password'] != password:
            config.set('User', 'password', str(password))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['serverip'] != server:
            config.set('server', 'serverip', str(server))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['serverport'] != port:
            config.set('server', 'serverport', str(port))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['udpipsend'] != udpipsend:
            config.set('udp', 'udpipsend', str(port))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['udpportsend'] != udpportsend:
            config.set('udp', 'udpportsend', str(port))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['udpipreceive'] != udpipreceive:
            config.set('udp', 'udpipreceive', str(port))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['udpportreceive'] != udpportreceive:
            config.set('udp', 'udpportreceive', str(port))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)

        self.close()


# Objects designed for output the information
class WriteStream(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass

#  A QObject (to be run in a QThread) which sits waiting
#  for data to come  through a Queue.Queue().
#  It blocks until data is available, and one it has got something from
#  the queue, it sends it to the "MainThread" by emitting a Qt Signal


class MyReceiver(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self, queue, *args, **kwargs):
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.queue = queue

    @QtCore.pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)


class ResultObj(QtCore.QObject):
    def __init__(self, val):
        self.val = val


if __name__ == '__main__':

    queue = Queue()
    sys.stdout = WriteStream(queue)

    log.startLogging(sys.stdout)
    log.msg('------------------------------------------------ ' +
            'SATNet - Generic client' +
            ' ------------------------------------------------')

    try:
        if sys.argv[1] == "-help":
            import subprocess
            subprocess.call(["man", "./satnetclient.1"])
        elif sys.argv[1] == "-g":
            import getopt
            try:
                opts, args = getopt.getopt(sys.argv[1:],
                                           "hfgn:p:t:c:s:b:is:us:ir:ur",
                                           ["name=", "password=",
                                            "slot=", "connection=",
                                            "serialport=",
                                            "baudrate=", "udpipsend=",
                                            "udpportsend=", "udpipreceive=",
                                            "udpportreceive="]
                                           )
            except getopt.GetoptError:
                print "error"

            argumentsDict = {}
            if ('-g', '') in opts:
                for opt, arg in opts:
                    if opt == "-n":
                        argumentsDict['username'] = arg
                    elif opt == "-p":
                        argumentsDict['password'] = arg
                    elif opt == "-t":
                        argumentsDict['slot'] = arg
                    elif opt == "-c":
                        argumentsDict['connection'] = arg
                    elif opt == "-s":
                        argumentsDict['serialport'] = arg
                    elif opt == "-b":
                        argumentsDict['baudrate'] = arg
                    elif opt == "-is":
                        argumentsDict['udpipsend'] = arg
                    elif opt == "-us":
                        argumentsDict['udpportsend'] = arg
                    elif opt == "-ir":
                        argumentsDict['udpipreceive'] = arg
                    elif opt == "-ur":
                        argumentsDict['udpportreceive'] = arg

            qapp = QtGui.QApplication(sys.argv)
            app = SATNetGUI(argumentsDict)
            app.setWindowIcon(QtGui.QIcon('icon.png'))
            app.show()

            # Create thread that will listen on the other end of the queue, and
            # send the text to the textedit in our application
            my_receiver = MyReceiver(queue)
            my_receiver.mysignal.connect(app.append_text)
            my_receiver.start()

            from qtreactor import pyqt4reactor
            pyqt4reactor.install()
            from twisted.internet import reactor
            reactor.run()
        elif sys.argv[1] != "-g" and sys.argv[1] != "-help":
            print "Unknown option: %s" % (sys.argv[1])
            print "Try 'python client_amp.py -help' for more information."
    except IndexError:
        argumentsDict = {}
        arguments = ['username', 'password', 'slot', 'connection',
                     'serialport', 'baudrate', 'udpipsend', 'udpportsend',
                     'udpipreceive', 'udpportreceive']
        for i in range(len(arguments)):
            argumentsDict[arguments[i]] = ""

        qapp = QtGui.QApplication(sys.argv)
        app = SATNetGUI(argumentsDict)
        app.setWindowIcon(QtGui.QIcon('icon.png'))
        app.show()

        # Create thread that will listen on the other end of the
        # queue, and send the text to the textedit in our application
        my_receiver = MyReceiver(queue)
        my_receiver.mysignal.connect(app.append_text)
        my_receiver.start()

        from qtreactor import pyqt4reactor
        pyqt4reactor.install()

        from twisted.internet import reactor
        reactor.run()
