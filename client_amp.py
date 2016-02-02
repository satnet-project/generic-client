# coding=utf-8
import sys
import os
import misc
import warnings

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

"""
    Notas. El problema viene de que no puedo enviar los datos desde la interfaz
    principal del programa.
    ¿Desde donde se envian los datos?
    ClientProtocl tendría que ser el encargado de llamar a la Functions
    de gs_interface

    Necesito gestionar una conexion serial, no una AMP así que las llamadas
    a _manageFrame no me valen. Tengo que sacar la gestion de las
    conexiones de la interfaz para así poder manejarlas.

    ¿De donde se manejan los callback?
    El metodo implementado actualmente lo unico que hace es escuchar
    permanenmente.

    Tengo que enviar una señal desde AMP hasta la el QThread
    """


class ClientProtocol(AMP):
    """
    Client class
    """

    def __init__(self, CONNECTION_INFO, gsi):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi

    def connectionMade(self):
        self.user_login()
        self.gsi.connectProtocol(self)

    def connectionLost(self, reason):
        log.msg("Connection lost")
        self.gsi.disconnectProtocol()

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

        sMessage = sMsg

        if self.CONNECTION_INFO['connection'] == 'serial':
            log.msg("Message received via serial")
            log.msg(sMessage)

            log.msg("antes del test")
            # self.gsi._manageFrame(sMessage)

            import kiss
            kissTNC = kiss.KISS(self.CONNECTION_INFO['serialport'],
                                self.CONNECTION_INFO['baudrate'])
            kissTNC.start()
            kissTNC.write(sMessage)

            log.msg("despues del test")

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'udp':
            log.msg(sMessage)

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'tcp':
            log.msg(sMessage)

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'none':
            log.msg(sMessage)

            log.msg("none")
            return {'bResult': True}

    NotifyMsg.responder(vNotifyMsg)

    # Method associated to frame processing.
    def _processframe(self, frame):
        frameProcessed = []
        frameProcessed = list(frame)
        frameProcessed = ":".join("{:02x}".format(ord(c))
                                  for c in frameProcessed)

        log.msg('Received frame: ', frameProcessed)

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
            # log.msg(sDetails)

        return {}
    NotifyEvent.responder(vNotifyEvent)


class ClientReconnectFactory(ReconnectingClientFactory):
    """
    ReconnectingClientFactory inherited object class to handle
    the reconnection process.
    """
    def __init__(self, CONNECTION_INFO, gsi):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi

    # Called when a connection has been started
    def startedConnecting(self, connector):
        log.msg("Starting connection............................" +
                "..............................................." +
                "..........................................")

    # Create an instance of a subclass of Protocol
    def buildProtocol(self, addr):
        log.msg("Building protocol.............................." +
                "..............................................." +
                "..........................")
        self.resetDelay()
        return ClientProtocol(self.CONNECTION_INFO, self.gsi)

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

        global connector
        connector = reactor.connectSSL(str(self.CONNECTION_INFO['serverip']),
                                       int(self.CONNECTION_INFO['serverport']),
                                       ClientReconnectFactory(
                                        self.CONNECTION_INFO,
                                        gsi),
                                       CtxFactory())

        return gsi, connector


class Threads(object):
    def __init__(self):
        pass


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

        self.serialSignal = True
        self.UDPSignal = True
        self.TCPSignal = True

        self.serial_queue = Queue()
        self.udp_queue = Queue()
        self.tcp_queue = Queue()

    # Run threads associated to KISS protocol
    def runKISSThread(self):
        self.workerKISSThread = OperativeKISSThread(self.serial_queue,
                                                    self.sendData,
                                                    self.serialSignal,
                                                    self.CONNECTION_INFO)
        self.workerKISSThread.start()

    def runUDPThreadReceive(self):
        self.workerUDPThreadReceive = OperativeUDPThreadReceive(self.udp_queue,
                                                                self.sendData,
                                                                self.UDPSignal,
                                                                self.CONNECTION_INFO)
        self.workerUDPThreadReceive.start()

    def runUDPThreadSend(self):
        self.workerUDPThreadSend = OperativeUDPThreadSend(self.udp_queue,
                                                          self.sendData,
                                                          self.UDPSignal,
                                                          self.CONNECTION_INFO)
        self.workerUDPThreadSend.start()

    # Run threads associated to TCP protocol
    def runTCPThread(self):
        self.workerTCPThread = OperativeTCPThread(self.tcp_queue,
                                                  self.sendData,
                                                  self.TCPSignal,
                                                  self.CONNECTION_INFO)
        self.workerTCPThread.start()

    # Stop KISS thread
    def stopKISSThread(self):
        self.workerKISSThread.stop()

    # Stop UDP thread
    def stopUDPThreadReceive(self):
        self.workerUDPThreadReceive.stop()

    # Stop UDP thread
    def stopUDPThreadSend(self):
        self.workerUDPThreadSend.stop()

    # Stop TCP thread
    def stopTCPThread(self):
        self.workerTCPThread.stop()

    # Gets a string but can't format it! To-do
    def sendData(self, result):
        self.gsi._manageFrame(result)

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
            self.CONNECTION_INFO['udpip'] = self.LabelIP.text()
            self.CONNECTION_INFO['udpport'] = int(self.LabelIPPort.text())
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
        if self.CONNECTION_INFO['connection'] == 'serial':
            self.runKISSThread()
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.runUDPThreadReceive()
            self.runUDPThreadSend()
        elif self.CONNECTION_INFO['connection'] == 'tcp':
            self.runTCPThread()
        elif self.CONNECTION_INFO['connection'] == 'none':
            pass
        else:
            log.err('Error choosing connection type')

        self.ButtonNew.setEnabled(False)
        self.ButtonCancel.setEnabled(True)
        self.LoadDefaultSettings.setEnabled(False)
        self.AutomaticReconnection.setEnabled(False)

    def initUI(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(".settings")
        parameters = config.get('Connection', 'parameters')
        name = config.get('Client', 'name')

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.setFixedSize(1300, 800)
        self.setWindowTitle("SATNet client - %s" % (name))

        if parameters == 'yes':
            self.LoadParameters(0)
        elif parameters == 'no':
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
            self.layout.addRow(QtGui.QLabel("Serial port:    "),
                               self.LabelSerialPort)
            self.LabelBaudrate = QtGui.QLineEdit()
            self.layout.addRow(QtGui.QLabel("Baudrate:       "),
                               self.LabelBaudrate)
            self.LabelIP = QtGui.QLineEdit()
            self.layout.addRow(QtGui.QLabel("SATNet host:    "),
                               self.LabelIP)
            self.LabelIPPort = QtGui.QLineEdit()
            self.layout.addRow(QtGui.QLabel("Port:       "),
                               self.LabelIPPort)
        else:
            if self.CONNECTION_INFO['connection'] == 'serial':
                self.LabelSerialPort = QtGui.QComboBox()
                self.LabelSerialPort.setFixedWidth(190)
                from glob import glob
                ports = glob('/dev/tty[A-Za-z]*')
                self.LabelSerialPort.addItems(ports)
                self.layout.addRow(QtGui.QLabel("Serial port:    "),
                                   self.LabelSerialPort)
                self.LabelBaudrate = QtGui.QLineEdit()
                self.LabelBaudrate.setFixedWidth(190)
                self.layout.addRow(QtGui.QLabel("Baudrate:       "),
                                   self.LabelBaudrate)
            elif self.CONNECTION_INFO['connection'] == 'udp':
                self.LabelIP = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Host:            "),
                                   self.LabelIP)
                self.LabelIPPort = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Port:       "),
                                   self.LabelIPPort)
            elif self.CONNECTION_INFO['connection'] == 'tcp':
                self.LabelIP = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Host:            "),
                                   self.LabelIP)
                self.LabelIPPort = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Port:       "),
                                   self.LabelIPPort)
            elif self.CONNECTION_INFO['connection'] == 'none':
                self.LabelIP = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("SATNet host:     "),
                                   self.LabelIP)
                self.LabelIPPort = QtGui.QLineEdit()
                self.layout.addRow(QtGui.QLabel("Port:       "),
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

        configuration.setTitle("Basic configuration")
        configuration.move(10, 380)

    def initLogo(self):
        # Logo.
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
        if argumentsDict['serialPort'] != "":
            index = self.LabelSerialPort.findText(argumentsDict['serialPort'])
            self.LabelSerialPort.setCurrentIndex(index)
        if argumentsDict['baudRate'] != "":
            self.LabelBaudrate.setText(argumentsDict['baudRate'])
        if argumentsDict['UDPIp'] != "":
            self.LabelIP.setText(argumentsDict['UDPIp'])
        if argumentsDict['UDPPort'] != "":
            self.LabelIPPort.setText(argumentsDict['UDPPort'])

    # Set parameters from CONNECTION_INFO dict.
    def setParameters(self):
        #  To-do. Improve try-except with errors catching.
        try:
            self.LabelUsername.setText(self.CONNECTION_INFO['username'])
        except Exception as e:
            log.err(e)
        try:
            self.LabelPassword.setText(self.CONNECTION_INFO['password'])
        except Exception as e:
            log.err(e)
        try:
            self.LabelSlotID.setText(self.CONNECTION_INFO['slot_id'])
        except Exception as e:
            log.err(e)
        try:
            index = self.LabelConnection.findText(self.CONNECTION_INFO['connection'])
            self.LabelConnection.setCurrentIndex(index)
        except Exception as e:
            log.err(e)

        #  To-do. Optimized!
        if self.CONNECTION_INFO['connection'] == 'serial':
            index = self.LabelSerialPort.findText(serialPort)
            self.LabelSerialPort.setCurrentIndex(index)
            self.LabelBaudrate.setText(self.CONNECTION_INFO['baudRate'])
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.LabelIP.setText(self.CONNECTION_INFO['udpip'])
            self.LabelIPPort.setText(self.CONNECTION_INFO['ipport'])
        elif self.CONNECTION_INFO['connection'] == 'tcp':
            self.LabelIP.setText(self.CONNECTION_INFO['tcpip'])
            self.LabelIPPort.setText(self.CONNECTION_INFO['ipport'])
        elif self.CONNECTION_INFO['connection'] == 'none':
            self.LabelIP.setText(self.CONNECTION_INFO['serverip'])
            self.LabelIPPort.setText(str(self.CONNECTION_INFO['serverport']))
        else:
            raise Exception

    def CloseConnection(self):
        if self.CONNECTION_INFO['connection'] == 'udp':
            try:
                self.stopUDPThreadReceive()
                self.stopUDPThreadSend()
                log.msg("Stopping UDP connection")
            except Exception as e:
                log.err(e)
                log.err("Can't stop UDP thread")

        if self.CONNECTION_INFO['connection'] == 'tcp':
            try:
                self.stopTCPThread()
                log.msg("Stopping TCP connection")
            except Exception as e:
                log.err(e)
                log.err("Can't stop TCP thread")

        if self.CONNECTION_INFO['connection'] == 'serial':
            try:
                self.stopKISSThread()
                log.msg("Stopping KISS connection")
            except Exception as e:
                log.err(e)
                log.err("Can't stop KISS thread")

        self.c.disconnect()

        self.ButtonNew.setEnabled(True)
        self.ButtonCancel.setEnabled(False)

    def UpdateFields(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read('.settings')

        self.CONNECTION_INFO['reconnection'] = config.get('Connection',
                                                          'reconnection')
        self.CONNECTION_INFO['parameters'] = config.get('Connection',
                                                        'parameters')
        self.CONNECTION_INFO['name'] = config.get('Client', 'name')
        self.CONNECTION_INFO['attempts'] = config.get('Client', 'attempts')
        self.CONNECTION_INFO['username'] = config.get('User', 'username')
        self.CONNECTION_INFO['password'] = config.get('User', 'password')
        self.CONNECTION_INFO['slot_id'] = config.get('User', 'slot_id')
        self.CONNECTION_INFO['connection'] = config.get('User', 'connection')

        self.CONNECTION_INFO['serialport'] = config.get('Serial',
                                                        'serialport')
        self.CONNECTION_INFO['baudrate'] = config.get('Serial',
                                                      'baudrate')
        self.CONNECTION_INFO['udpip'] = config.get('udp', 'udpip')
        self.CONNECTION_INFO['udpport'] = int(config.get('udp',
                                                         'udpport'))
        self.CONNECTION_INFO['tcpip'] = config.get('tcp', 'tcpip')
        self.CONNECTION_INFO['tcpport'] = int(config.get('tcp',
                                                         'tcpport'))
        self.CONNECTION_INFO['serverip'] = config.get('server',
                                                      'serverip')
        self.CONNECTION_INFO['serverport'] = int(config.get('server',
                                                 'serverport'))

        #  To-do. Improve try-except with errors catching.
        try:
            self.LabelUsername.setText(self.CONNECTION_INFO['username'])
        except Exception as e:
            log.err(e)
        try:
            self.LabelPassword.setText(self.CONNECTION_INFO['password'])
        except Exception as e:
            log.err(e)
        try:
            self.LabelSlotID.setText(self.CONNECTION_INFO['slot_id'])
        except Exception as e:
            log.err(e)
        try:
            index = self.LabelConnection.findText(self.CONNECTION_INFO['connection'])
            self.LabelConnection.setCurrentIndex(index)
        except Exception as e:
            log.err(e)

        #  To-do. Optimized!
        if self.CONNECTION_INFO['connection'] == 'serial':
            index = self.LabelSerialPort.findText(serialPort)
            self.LabelSerialPort.setCurrentIndex(index)
            self.LabelBaudrate.setText(baudRate)
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.LabelIP.setText(self.CONNECTION_INFO['udpip'])
            self.LabelIPPort.setText(self.CONNECTION_INFO['ipport'])
        elif self.CONNECTION_INFO['connection'] == 'tcp':
            self.LabelIP.setText(self.CONNECTION_INFO['tcpip'])
            self.LabelIPPort.setText(self.CONNECTION_INFO['ipport'])
        elif self.CONNECTION_INFO['connection'] == 'none':
            self.LabelIP.setText(self.CONNECTION_INFO['serverip'])
            self.LabelIPPort.setText(str(self.CONNECTION_INFO['serverport']))
        else:
            raise Exception

    # Load connection parameters from .settings file.
    def LoadParameters(self, init_flag):
        self.CONNECTION_INFO = {}
        if init_flag == 1:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read('.settings')

            self.CONNECTION_INFO['reconnection'] = config.get('Connection',
                                                              'reconnection')
            self.CONNECTION_INFO['parameters'] = config.get('Connection',
                                                            'parameters')
            self.CONNECTION_INFO['name'] = config.get('Client', 'name')
            self.CONNECTION_INFO['attempts'] = config.get('Client', 'attempts')
            self.CONNECTION_INFO['username'] = config.get('User', 'username')
            self.CONNECTION_INFO['password'] = config.get('User', 'password')
            self.CONNECTION_INFO['slot_id'] = config.get('User', 'slot_id')
            self.CONNECTION_INFO['connection'] = str(self.LabelConnection.currentText())

            self.CONNECTION_INFO['serialport'] = config.get('Serial',
                                                            'serialport')
            self.CONNECTION_INFO['baudrate'] = config.get('Serial',
                                                          'baudrate')
            self.CONNECTION_INFO['udpip'] = config.get('udp', 'udpip')
            self.CONNECTION_INFO['udpport'] = int(config.get('udp',
                                                             'udpport'))
            self.CONNECTION_INFO['tcpip'] = config.get('tcp', 'tcpip')
            self.CONNECTION_INFO['tcpport'] = int(config.get('tcp',
                                                             'tcpport'))
            self.CONNECTION_INFO['serverip'] = config.get('server',
                                                          'serverip')
            self.CONNECTION_INFO['serverport'] = int(config.get('server',
                                                     'serverport'))

        elif init_flag == 0:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read('.settings')

            self.CONNECTION_INFO['reconnection'] = config.get('Connection',
                                                              'reconnection')
            self.CONNECTION_INFO['parameters'] = config.get('Connection',
                                                            'parameters')
            self.CONNECTION_INFO['name'] = config.get('Client', 'name')
            self.CONNECTION_INFO['attempts'] = config.get('Client', 'attempts')
            self.CONNECTION_INFO['username'] = config.get('User', 'username')
            self.CONNECTION_INFO['password'] = config.get('User', 'password')
            self.CONNECTION_INFO['slot_id'] = config.get('User', 'slot_id')
            self.CONNECTION_INFO['connection'] = config.get('User', 'connection')

            self.CONNECTION_INFO['serialport'] = config.get('Serial',
                                                            'serialport')
            self.CONNECTION_INFO['baudrate'] = config.get('Serial',
                                                          'baudrate')
            self.CONNECTION_INFO['udpip'] = config.get('udp', 'udpip')
            self.CONNECTION_INFO['udpport'] = int(config.get('udp',
                                                             'udpport'))
            self.CONNECTION_INFO['tcpip'] = config.get('tcp', 'tcpip')
            self.CONNECTION_INFO['tcpport'] = int(config.get('tcp',
                                                             'tcpport'))
            self.CONNECTION_INFO['serverip'] = config.get('server',
                                                          'serverip')
            self.CONNECTION_INFO['serverport'] = int(config.get('server',
                                                     'serverport'))
        elif init_flag == 2:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read('.settings')

            self.CONNECTION_INFO['reconnection'] = config.get('Connection',
                                                              'reconnection')
            self.CONNECTION_INFO['parameters'] = config.get('Connection',
                                                            'parameters')
            self.CONNECTION_INFO['name'] = config.get('Client', 'name')
            self.CONNECTION_INFO['attempts'] = config.get('Client', 'attempts')
            self.CONNECTION_INFO['username'] = config.get('User', 'username')
            self.CONNECTION_INFO['password'] = config.get('User', 'password')
            self.CONNECTION_INFO['slot_id'] = config.get('User', 'slot_id')
            self.CONNECTION_INFO['connection'] = config.get('User', 
                                                            'connection')

            self.CONNECTION_INFO['serialport'] = config.get('Serial',
                                                            'serialport')
            self.CONNECTION_INFO['baudrate'] = config.get('Serial',
                                                          'baudrate')
            self.CONNECTION_INFO['udpip'] = config.get('udp', 'udpip')
            self.CONNECTION_INFO['udpport'] = int(config.get('udp',
                                                             'udpport'))
            self.CONNECTION_INFO['tcpip'] = config.get('tcp', 'tcpip')
            self.CONNECTION_INFO['tcpport'] = int(config.get('tcp',
                                                             'tcpport'))
            self.CONNECTION_INFO['serverip'] = config.get('server',
                                                          'serverip')
            self.CONNECTION_INFO['serverport'] = int(config.get('server',
                                                     'serverport'))
        else:
            log.msg("Error")

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
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(".settings")

        username = config.get('User', 'username')
        self.LabelUsername.setText(username)
        password = config.get('User', 'password')
        self.LabelPassword.setText(password)

        self.LoadParameters(1)

        self.LabelSlotID.setFixedWidth(190)
        self.LabelConnection.setFixedWidth(190)

        if str(self.LabelConnection.currentText()) == 'serial':
            self.deleteMenu()

            self.LabelSerialPort = QtGui.QComboBox()
            self.LabelSerialPort.setFixedWidth(190)

            from glob import glob
            ports = glob('/dev/tty[A-Za-z]*')
            self.LabelSerialPort.addItems(ports)
            self.layout.addRow(QtGui.QLabel("Serial port:    "),
                               self.LabelSerialPort)
            self.LabelBaudrate = QtGui.QLineEdit()
            self.LabelBaudrate.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("Baudrate:       "),
                               self.LabelBaudrate)

            index = self.LabelSerialPort.findText(self.CONNECTION_INFO['serialport'])
            self.LabelSerialPort.setCurrentIndex(index)
            self.LabelBaudrate.setText(self.CONNECTION_INFO['baudrate'])

        elif str(self.LabelConnection.currentText()) == 'udp':
            self.deleteMenu()

            self.LabelIP = QtGui.QLineEdit()
            self.LabelIP.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("UDP host:        "), self.LabelIP)
            self.LabelIPPort = QtGui.QLineEdit()
            self.LabelIPPort.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("Port:       "), self.LabelIPPort)

            # Gets data from .settings file not from user interface
            # To-do
            ip = config.get('udp', 'udpip')
            self.LabelIP.setText(ip)
            udpport = int(config.get('udp', 'udpport'))
            self.LabelIPPort.setText(str(udpport))

        elif str(self.LabelConnection.currentText()) == 'tcp':
            self.deleteMenu()

            self.LabelIP = QtGui.QLineEdit()
            self.LabelIP.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("TCP host:        "), self.LabelIP)
            self.LabelIPPort = QtGui.QLineEdit()
            self.LabelIPPort.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("Port:       "), self.LabelIPPort)

            # Gets data from .settings file not from user interface
            # To-do
            ip = config.get('tcp', 'tcpip')
            self.LabelIP.setText(ip)
            tcpport = int(config.get('tcp', 'tcpport'))
            self.LabelIPPort.setText(str(tcpport))

        elif str(self.LabelConnection.currentText()) == 'none':
            self.deleteMenu()

            self.LabelIP = QtGui.QLineEdit()
            self.LabelIP.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("SATNet server:"),
                               self.LabelIP)
            self.LabelIPPort = QtGui.QLineEdit()
            self.LabelIPPort.setFixedWidth(190)
            self.layout.addRow(QtGui.QLabel("Port:       "),
                               self.LabelIPPort)

            ip = config.get('server', 'serverip')
            self.LabelIP.setText(ip)
            serverport = int(config.get('server', 'serverport'))
            self.LabelIPPort.setText(str(serverport))

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
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
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
                # Connector disconnected
                self.c.disconnect()
            except Exception as e:
                pass

            try:
                if self.CONNECTION_INFO['connection'] == 'udp':
                    try:
                        self.stopUDPThread()
                    except Exception as e:
                        log.err(e)
                        log.err("Can't stop UDP thread")

                elif self.CONNECTION_INFO['connection'] == 'tcp':
                    try:
                        self.stopTCPThread()
                    except Exception as e:
                        log.err(e)
                        log.err("Can't stop TCP thread")

                elif self.CONNECTION_INFO['connection'] == 'serial':
                    try:
                        self.stopKISSThread()
                    except Exception as e:
                        log.err(e)
                        log.err("Can't stop KISS thread")
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
            pass


class ConfigurationWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ConfigurationWindow, self).__init__(parent)

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

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)

        buttonBox.button(QtGui.QDialogButtonBox.Close).clicked.connect(self.closeWindow)
        buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self.save)

        grid.addWidget(LabelClientname, 0, 0, 1, 1)
        grid.addWidget(self.FieldClientname, 0, 1, 1, 1)
        grid.addWidget(LabelPassword, 1, 0, 1, 1)
        grid.addWidget(self.FieldLabelPassword, 1, 1, 1, 1)
        grid.addWidget(LabelServer, 2, 0, 1, 1)
        grid.addWidget(self.FieldLabelServer, 2, 1, 1, 1)
        grid.addWidget(LabelPort, 3, 0, 1, 1)
        grid.addWidget(self.FieldLabelPort, 3, 1, 1, 1)
        grid.addWidget(buttonBox, 4, 0, 1, 2)

        self.setMinimumSize(405, 260)
        parameters.setTitle("Connection")
        parameters.move(10, 10)

        # Read fields
        name, password, server, port = self.readFields()
        self.FieldClientname.setText(name)
        self.FieldLabelPassword.setText(password)
        self.FieldLabelServer.setText(server)
        self.FieldLabelPort.setText(port)

    def closeWindow(self):
        self.close()

    def readFields(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(".settings")
        name = config.get('User', 'username')
        password = config.get('User', 'password')
        server = config.get('server', 'serverip')
        port = config.get('server', 'serverport')

        return name, password, server, port

    def save(self):
        import ConfigParser
        config = ConfigParser.SafeConfigParser()
        config.read(".settings")

        name = self.FieldClientname.text()
        password = self.FieldLabelPassword.text()
        server = self.FieldLabelServer.text()
        port = self.FieldLabelPort.text()

        nameSet, passwordSet, serverSet, portSet = self.readFields()
        if nameSet != name:
            config.set('User', 'username', str(name))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if passwordSet != password:
            config.set('User', 'password', str(password))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if serverSet != server:
            config.set('server', 'serverip', str(server))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if portSet != port:
            config.set('server', 'serverport', str(port))
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

    try:
        if sys.argv[1] == "-help":
            import subprocess
            subprocess.call(["man", "./satnetclient.1"])
        elif sys.argv[1] == "-g":
            import getopt
            try:
                opts, args = getopt.getopt(sys.argv[1:],
                                           "hfgn:p:t:c:s:b:i:u:",
                                           ["name=", "password=",
                                            "slot=", "connection=",
                                            "serialport=",
                                            "baudrate=", "ip=",
                                            "udpport="]
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
                        argumentsDict['serialPort'] = arg
                    elif opt == "-b":
                        argumentsDict['baudRate'] = arg
                    elif opt == "-i":
                        argumentsDict['UDPIp'] = arg
                    elif opt == "-u":
                        argumentsDict['UDPPort'] = arg

            queue = Queue()
            sys.stdout = WriteStream(queue)

            log.startLogging(sys.stdout)
            log.msg('------------------------------------------------- ' +
                    'SATNet - Generic client' +
                    ' -------------------------------------------------')

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
                     'serialPort', 'baudRate', 'UDPIp', 'UDPPort']
        for i in range(len(arguments)):
            argumentsDict[arguments[i]] = ""

        queue = Queue()
        sys.stdout = WriteStream(queue)

        log.startLogging(sys.stdout)
        log.msg('----------------------------------------------- ' +
                'SATNet - Generic client' +
                ' -----------------------------------------------')

        qapp = QtGui.QApplication(sys.argv)
        app = SATNetGUI(argumentsDict)
        app.setWindowIcon(QtGui.QIcon('icono.png'))
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
