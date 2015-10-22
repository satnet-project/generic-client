# coding=utf-8
"""
   Copyright 2014, 2015 Xabier Crespo Álvarez

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
    Xabier Crespo Álvarez (xabicrespog@gmail.com)
"""
__author__ = 'xabicrespog@gmail.com'


import sys
import os

from OpenSSL import SSL
from PyQt4 import QtGui
from PyQt4 import QtCore

from twisted.python import log
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.amp import AMP
from twisted.cred.credentials import UsernamePassword
from twisted.internet.defer import inlineCallbacks
from twisted.python.logfile import DailyLogFile

from protocol.ampauth.login import Login
from protocol.ampCommands import EndRemote
from protocol.ampCommands import StartRemote
from protocol.ampCommands import NotifyMsg
from protocol.ampCommands import NotifyEvent

from gs_interface import GroundStationInterface
import getpass
import getopt
import threading
import misc


class ClientProtocol(AMP):

    def __init__(self, CONNECTION_INFO, gsi):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi

    def connectionMade(self):
        self.user_login()
        self.gsi.connectProtocol(self)

    def connectionLost(self, reason):
        log.err("Connection lost")
        log.err(reason)
        self.gsi.disconnectProtocol()
        res = yield self.callRemote(EndRemote)

    @inlineCallbacks
    def user_login(self):        
        try:
            res = yield self.callRemote(Login,\
             sUsername=self.CONNECTION_INFO['username'],\
              sPassword=self.CONNECTION_INFO['password'])
            res = yield self.callRemote(StartRemote,\
             iSlotId=self.CONNECTION_INFO['slot_id'])
        except Exception as e:
            log.err(e)
            reactor.stop()

    def vNotifyMsg(self, sMsg):
        log.msg("(" + self.CONNECTION_INFO['username'] +\
         ") --------- Notify Message ---------")
        log.msg(sMsg)
        if self.CONNECTION_INFO['connection'] == 'serial':        
            self.kissTNC.write(sMsg)
        # Only serial communications are needed.
        """
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.UDPSocket.sendto(sMsg, (self.CONNECTION_INFO['ip'],\
             self.CONNECTION_INFO['udpport']))
        """
        return {}
    NotifyMsg.responder(vNotifyMsg)

    def processFrame(self, frame):
        log.msg('Received frame: ' + frame)
        res = self.callRemote(SendMsg, sMsg=frame,\
         iTimestamp=misc.get_utc_timestamp())
        log.msg(res)

    def vNotifyEvent(self, iEvent, sDetails):
        log.msg("(" + self.CONNECTION_INFO['username'] +\
         ") --------- Notify Event ---------")
        if iEvent == NotifyEvent.SLOT_END:
            log.msg("Disconnection because the slot has ended")
        elif iEvent == NotifyEvent.REMOTE_DISCONNECTED:
            log.msg("Remote client has lost the connection")
        elif iEvent == NotifyEvent.END_REMOTE:
            log.msg("The remote client has closed the connection")
        elif iEvent == NotifyEvent.REMOTE_CONNECTED:
            log.msg("The remote client has just connected")

        return {}
    NotifyEvent.responder(vNotifyEvent)


class ClientReconnectFactory(ReconnectingClientFactory):
    """
    ReconnectingClientFactory inherited object class to handle the 
    reconnection process.

    """
    def __init__(self, CONNECTION_INFO, gsi):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi
        # self.continueTrying = 0

    def startedConnecting(self, connector):
        log.msg('Starting connection...')

    def buildProtocol(self, addr):
        log.msg('Building protocol...')
        self.resetDelay()
        return ClientProtocol(self.CONNECTION_INFO, self.gsi)

    def clientConnectionLost(self, connector, reason):
        """
        self.CONNECTION_INFO ok
        """
        self.continueTrying = None

        log.msg('Lost connection. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionLost(self,\
         connector, reason)

    def clientConnectionFailed(self, connector, reason):
        """
        self.CONNECTION_INFO ok
        """
        self.continueTrying = None

        log.msg('Connection failed. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionFailed(self,\
         connector, reason)


class Client():
    """
    This class starts the client using the data provided by user interface.

    :ivar CONNECTION_INFO:
        This variable contains the following data: username, password, slot_id, 
        connection (either 'serial' or 'udp'), serialport, baudrate, ip, port.
    :type CONNECTION_INFO:
        L{Dictionary}

    :ivar

    """
    def __init__(self, CONNECTION_INFO):
        self.CONNECTION_INFO = CONNECTION_INFO

    def createConnection(self):
        gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo")

        global connector

        connector = reactor.connectSSL('localhost', 1234,\
         ClientReconnectFactory(self.CONNECTION_INFO, gsi),\
          ClientContextFactory())

        return connector


"""
Really we need to use QtGui.QMainWindow class. For time reasons we 
maintain QtGui.QWidget although is not the right way.
class SatNetGUI(QtGui.QMainWindow):
"""

class SatNetGUI(QtGui.QWidget):
    """
    This class creates an object of class QtGui.QWidget to the main window.

    """

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ConfigurationWindow = None
        self.initUI()
        self.center()

    def initUI(self):
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.setFixedSize(1300, 800)
        self.setWindowTitle("SATNet client - Generic") 

        # Control buttons.
        buttons = QtGui.QGroupBox(self)
        grid = QtGui.QGridLayout(buttons)
        buttons.setLayout(grid)

        # New connection.
        ButtonNew = QtGui.QPushButton("Connect")
        ButtonNew.setToolTip("Start a new connection")
        ButtonNew.setFixedWidth(145)
        # ButtonNew.setCheckable(True)
        ButtonNew.clicked.connect(self.NewConnection)
        # Close connection.
        ButtonCancel = QtGui.QPushButton("Disconnect")
        ButtonCancel.setToolTip("End current connection")
        ButtonCancel.setFixedWidth(145)
        ButtonCancel.clicked.connect(self.CloseConnection)
        # Load parameters from file
        ButtonLoad = QtGui.QPushButton("Load parameters from file")
        ButtonLoad.setToolTip("Load parameters from <i>config.ini</i> file")
        ButtonLoad.setFixedWidth(298)
        ButtonLoad.clicked.connect(self.LoadParameters)
        # Configuration
        ButtonConfiguration = QtGui.QPushButton("Configuration")
        ButtonConfiguration.setToolTip("Set configuration")
        ButtonConfiguration.setFixedWidth(145)
        ButtonConfiguration.clicked.connect(self.SetConfiguration)
        # Help.
        ButtonHelp = QtGui.QPushButton("Help")
        ButtonHelp.setToolTip("Click for help")
        ButtonHelp.setFixedWidth(145)
        ButtonHelp.clicked.connect(self.usage)

        grid.addWidget(ButtonNew, 0, 0, 1, 1)
        grid.addWidget(ButtonCancel, 0, 1, 1, 1)
        grid.addWidget(ButtonLoad, 1, 0, 1, 2)
        grid.addWidget(ButtonConfiguration, 2, 0, 1, 1)
        grid.addWidget(ButtonHelp, 2, 1, 1, 1)
        buttons.setTitle("Connection")
        buttons.move(10, 10)

        # Parameters group.
        parameters = QtGui.QGroupBox(self)
        layout = QtGui.QFormLayout()
        parameters.setLayout(layout)

        self.LabelUsername = QtGui.QLineEdit()
        self.LabelUsername.setFixedWidth(190)
        layout.addRow(QtGui.QLabel("Username:       "), self.LabelUsername)
        self.LabelPassword = QtGui.QLineEdit()
        self.LabelPassword.setFixedWidth(190)
        self.LabelPassword.setEchoMode(QtGui.QLineEdit.Password)
        layout.addRow(QtGui.QLabel("Password:       "), self.LabelPassword)
        self.LabelSlotID = QtGui.QSpinBox()
        layout.addRow(QtGui.QLabel("slot_id:        "), self.LabelSlotID)

        self.LabelConnection = QtGui.QComboBox()
        self.LabelConnection.addItems(['serial', 'udp'])
        self.LabelConnection.activated.connect(self.CheckConnection)
        layout.addRow(QtGui.QLabel("Connection:     "), self.LabelConnection)
        self.LabelSerialPort = QtGui.QComboBox()
        from glob import glob
        ports = glob('/dev/tty[A-Za-z]*')
        self.LabelSerialPort.addItems(ports)
        layout.addRow(QtGui.QLabel("Serial port:    "), self.LabelSerialPort)
        self.LabelBaudrate = QtGui.QLineEdit()
        layout.addRow(QtGui.QLabel("Baudrate:       "), self.LabelBaudrate)
        self.LabelUDP = QtGui.QLineEdit()
        layout.addRow(QtGui.QLabel("UDP:            "), self.LabelUDP)
        self.LabelUDPPort = QtGui.QLineEdit()
        layout.addRow(QtGui.QLabel("UDP port:       "), self.LabelUDPPort)

        parameters.setTitle("User data")
        parameters.move(10, 145)

        # Configuration group.
        configuration = QtGui.QGroupBox(self)
        configurationLayout = QtGui.QVBoxLayout()
        configuration.setLayout(configurationLayout)

        self.LoadDefaultSettings =\
         QtGui.QCheckBox("Automatically load settings from 'config.ini'")
        configurationLayout.addWidget(self.LoadDefaultSettings)
        self.AutomaticReconnection =\
         QtGui.QCheckBox("Reconnect after a failure")
        configurationLayout.addWidget(self.AutomaticReconnection)

        configuration.setTitle("Basic configuration")
        configuration.move(10, 400)

        # Logo.
        self.LabelLogo = QtGui.QLabel(self)
        self.LabelLogo.move(20, 490)
        pic = QtGui.QPixmap(os.getcwd() + "/logo.png")
        self.LabelLogo.setPixmap(pic)
        self.LabelLogo.show()

        # Console
        console = QtGui.QTextBrowser(self)
        console.move(340, 10)
        console.resize(950, 780)
        console.setFont(QtGui.QFont('SansSerif', 10))

        XStream.stdout().messageWritten.connect(console.insertPlainText)
        XStream.stderr().messageWritten.connect(console.insertPlainText)

        try:
            opts, args = getopt.getopt(sys.argv[1:],"hfgu:p:t:c:s:b:i:u:",\
             ["username=", "password=", "slot=", "connection=", "serialport=",\
              "baudrate=", "ip=", "udpport="])
        except getopt.GetoptError:
            print "error"

        if ('-g', '') in opts:
            for opt, arg in opts:
                if opt == "-u":
                    self.LabelUsername.setText(arg)
                elif opt == "-p":
                    self.LabelPassword.setText(arg)
                elif opt == "-t":
                    self.LabelSlotID.setValue(arg)
                elif opt == "-c":
                    index = self.LabelConnection.findText(arg)
                    self.LabelConnection.setCurrentIndex(index)
                elif opt == "-s":
                    index = self.LabelSerialPort.findText(arg)
                    self.LabelSerialPort.setCurrentIndex(index)
                elif opt == "-b":
                    self.LabelBaudrate.setText(arg)
                elif opt == "-i":
                    self.LabelUDP.setText(arg)
                elif opt == "-u":
                    self.LabelUDPPort.setText(arg)

        reconnection, parameters = self.LoadSettings()
        if reconnection == 'yes':
            self.AutomaticReconnection.setChecked(True)
        elif reconnection == 'no':
            self.AutomaticReconnection.setChecked(False)
        if parameters == 'yes':
            self.LoadDefaultSettings.setChecked(True)
            self.LoadParameters()
        elif parameters == 'no':
            self.LoadDefaultSettings.setChecked(False)

    def NewConnection(self):
        """
        Create a new connection by loading the connection parameters from 
        the command line or from the interface window.

        """
        self.CONNECTION_INFO = {}

        try:
            opts, args = getopt.getopt(sys.argv[1:],"hfgu:p:t:c:s:b:i:u:",\
             ["username=", "password=", "slot=", "connection=", "serialport=",\
              "baudrate=", "ip=", "udpport="])
        except getopt.GetoptError:
            print "error"

        if ('-g','') in opts:
            for opt, arg in opts:
                if opt in ("-u", "--username"):
                    self.CONNECTION_INFO['username']  = arg
                elif opt in ("-p", "--password"):
                    self.CONNECTION_INFO['password']  = arg
                elif opt in ("-t", "--slot"):
                    self.CONNECTION_INFO['slot_id']  = arg
                elif opt in ("-c", "--connection"):
                    self.CONNECTION_INFO['connection'] = arg
                elif opt in ("-s", "--serialport"):
                    self.CONNECTION_INFO['serialport']  = arg
                elif opt in ("-b", "--baudrate"):
                    self.CONNECTION_INFO['baudrate']  = arg
                elif opt in ("-i", "--ip"):
                    self.CONNECTION_INFO['ip']  = arg
                elif opt in ("-u", "--udpport"):
                    self.CONNECTION_INFO['udpport']  = int(arg)
            self.paramValidation()

        else:
            self.CONNECTION_INFO['username'] = str(self.LabelUsername.text())
            self.CONNECTION_INFO['password'] = str(self.LabelPassword.text())
            self.CONNECTION_INFO['slot_id'] = int(self.LabelSlotID.text())
            self.CONNECTION_INFO['connection'] =\
             str(self.LabelConnection.currentText())
            self.CONNECTION_INFO['serialport'] =\
             str(self.LabelSerialPort.currentText())
            self.CONNECTION_INFO['baudrate'] = str(self.LabelBaudrate.text())
            self.CONNECTION_INFO['ip'] = self.LabelUDP.text()
            print self.LabelUDPPort.text()
            # self.CONNECTION_INFO['udpport'] = int(self.LabelUDPPort.text())

        self.c = Client(self.CONNECTION_INFO).createConnection()


    # To-do. Not closed properly.
    def CloseConnection(self):
        """
        Closes the connection in a fancy way.
        """
        try:
            self.c.disconnect()
        except Exception:
            log.msg('Already stopped.')

    def LoadSettings(self):
        """
        Load settings from .settings file.
        """
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(".settings")

        reconnection = config.get('Connection', 'reconnection')
        parameters = config.get('Connection', 'parameters')

        return reconnection, parameters

    def LoadParameters(self):
        """
        Load connection parameters from config.ini file.
        """
        self.CONNECTION_INFO = {}

        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read("config.ini")

        self.CONNECTION_INFO['username'] = config.get('User', 'username')
        self.LabelUsername.setText(self.CONNECTION_INFO['username'])
        self.CONNECTION_INFO['password'] = config.get('User', 'password')
        self.LabelPassword.setText(self.CONNECTION_INFO['password'])
        self.CONNECTION_INFO['slot_id'] = config.get('User', 'slot_id')
        self.LabelSlotID.setValue(int(self.CONNECTION_INFO['slot_id']))        
        self.CONNECTION_INFO['connection'] = config.get('User', 'connection')
        index = self.LabelConnection.findText(self.CONNECTION_INFO['connection'])
        self.LabelConnection.setCurrentIndex(index)

        if self.CONNECTION_INFO['connection'] == 'serial':
            self.LabelSerialPort.setEnabled(True)
            self.LabelBaudrate.setEnabled(True)
            self.LabelUDP.setEnabled(False)
            self.LabelUDPPort.setEnabled(False)
            self.CONNECTION_INFO['serialport'] = config.get('Serial',\
             'serialport')
            index = self.LabelSerialPort.findText(self.CONNECTION_INFO['serialport'])
            self.LabelSerialPort.setCurrentIndex(index)
            self.CONNECTION_INFO['baudrate'] = config.get('Serial',\
             'baudrate')
            self.LabelBaudrate.setText(self.CONNECTION_INFO['baudrate'])

        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.LabelSerialPort.setEnabled(False)
            self.LabelBaudrate.setEnabled(False)
            self.LabelUDP.setEnabled(True)
            self.LabelUDPPort.setEnabled(True)
            self.CONNECTION_INFO['ip'] = config.get('UDP', 'ip')
            self.LabelUDP.setText(self.CONNECTION_INFO['ip'])
            self.CONNECTION_INFO['udpport'] = int(config.get('UDP',\
             'udpport'))
            self.LabelUDPPort.setText(config.get('UDP', 'udpport'))

    def SetConfiguration(self):
        self.ConfigurationWindow = ConfigurationWindow()
        self.ConfigurationWindow.show()

    def CheckConnection(self):
        Connection = str(self.LabelConnection.currentText())

        if Connection == 'serial':
            self.LabelSerialPort.setEnabled(True)
            self.LabelBaudrate.setEnabled(True)
            self.LabelUDP.setEnabled(False)
            self.LabelUDPPort.setEnabled(False)
        elif Connection == 'udp':
            self.LabelSerialPort.setEnabled(False)
            self.LabelBaudrate.setEnabled(False)
            self.LabelUDP.setEnabled(True)
            self.LabelUDPPort.setEnabled(True)

    def paramValidation(self):
        # Parameters validation
        if 'username' not in self.CONNECTION_INFO:
            log.err('Missing username parameter [-u username]')
            exit()
        if 'password' not in self.CONNECTION_INFO:
            log.err('Missing username parameter [-p password]')
            exit()
        if 'connection' not in self.CONNECTION_INFO:
            log.err('Missing connection parameter [-c serial] or [-c udp]')
            exit()
        if self.CONNECTION_INFO['connection'] == 'serial':
            log.msg('Using a serial interface with the GS')
            if 'serialport' not in self.CONNECTION_INFO or 'baudrate' not in self.CONNECTION_INFO:
                log.msg('Missing some client configurations (serialport [-s] or baudrate [-b])')
                exit()
        if self.CONNECTION_INFO['connection'] == 'udp':
            log.msg('Using an UDP interface with the GS')
            if 'ip' not in self.CONNECTION_INFO or 'udpport' not in self.CONNECTION_INFO:
                log.msg('Missing some client configurations (ip [-i] or udpport [-u])')
                exit()

    def usage(self):
        print ("\n"
                "USAGE of client_amp.py\n"               
                "Usage: python client_amp.py [-u <username>] # Set SATNET username to login\n"
                "Usage: python client_amp.py [-p <password>] # Set SATNET user password to login\n"
                "Usage: python client_amp.py [-t <slot_ID>] # Set the slot id corresponding to the pass you will track\n"
                "Usage: python client_amp.py [-c <connection>] # Set the type of interface with the GS (serial or udp)\n"
                "Usage: python client_amp.py [-s <serialport>] # Set serial port\n"
                "Usage: python client_amp.py [-b <baudrate>] # Set serial port baudrate\n"
                "Usage: python client_amp.py [-i <ip>] # Set ip direction\n"
                "Usage: python client_amp.py [-u <udpport>] # Set udp port\n"
                "\n"
                "Example for serial config: python client_amp.py -g -u crespo -p cre.spo -t 2 -c serial -s /dev/ttyS1 -b 115200\n"
                "Example for udp config: python client_amp.py -g -u crespo -p cre.spo -t 2 -c udp -i 127.0.0.1 -u 5001\n"
                "\n"
                "[User]\n"
                "username: crespo\n"
                "password: cre.spo\n"
                "slot_id: 2\n"
                "connection: udp\n"
                "[Serial]\n"
                "serialport: /dev/ttyUSB0\n"
                "baudrate: 9600\n"
                "[UDP]\n"
                "ip: 127.0.0.1\n"
                "udpport: 5005")

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def closeEvent(self, event):
        
        reply = QtGui.QMessageBox.question(self, 'Exit confirmation',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            try:
                self.c.disconnect()
                reactor.stop()
            except Exception:
                log.msg("Reactor not running.")

            event.accept()
        else:
            event.ignore()  


class XStream(QtCore.QObject):
    """

    This class creates an object of class QtCore.QObject to 
    display announcements.

    """
    _stdout = None
    _stderr = None

    messageWritten = QtCore.pyqtSignal(str)

    def flush( self ):
        pass

    def fileno( self ):
        return -1

    def write( self, msg ):
        if ( not self.signalsBlocked() ):
            self.messageWritten.emit(unicode(msg))

    @staticmethod
    def stdout():
        if ( not XStream._stdout ):
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if ( not XStream._stderr ):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


class ConfigurationWindow(QtGui.QWidget):
    """

    This class creates a new window where you can set the 
    connection parameters.

    """
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.initUI()
        self.center()

    def initUI(self):
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 11))
        self.setFixedSize(350, 135)
        self.setWindowTitle("Configuration window")

        configuration = QtGui.QGroupBox(self)
        layout = QtGui.QFormLayout()
        configuration.setLayout(layout)

        self.LabelMaxRetries = QtGui.QLineEdit()
        self.LabelMaxRetries.setFixedWidth(150)
        layout.addRow(QtGui.QLabel("Maximum retries:         "),\
         self.LabelMaxRetries)
        self.LabelDelay = QtGui.QLineEdit()
        self.LabelDelay.setFixedWidth(150)
        layout.addRow(QtGui.QLabel("Password:                "),\
         self.LabelDelay)

        configuration.setTitle("User data")
        configuration.move(10, 10)

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


if __name__ == '__main__':
    
    log.startLogging(DailyLogFile.fromFullPath("foo.log"))

    # log.startLogging(sys.stdout)
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('logo.png'))
    window = SatNetGUI()
    window.show()

    """
    Using a specific reactor implementation, pyqt4reactor
    """
    from qtreactor import pyqt4reactor
    pyqt4reactor.install()

    from twisted.internet import reactor
    reactor.run()

    sys.exit(app.exec_())
