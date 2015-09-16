# coding=utf-8
"""
   Copyright 2014 Xabier Crespo Álvarez

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

from OpenSSL import SSL
from PyQt4 import QtGui, QtCore

from twisted.python import log
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.amp import AMP
from twisted.cred.credentials import UsernamePassword
from twisted.internet.defer import inlineCallbacks

from protocol.ampauth.commands import Login
from protocol.commands import StartRemote, NotifyMsg, NotifyEvent
from protocol.errors import *

from gs_interface import GroundStationInterface
import getpass, getopt, threading
import misc

import os

class ClientProtocol(AMP):

    CONNECTION_INFO = {}

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
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.UDPSocket.sendto(sMsg, (self.CONNECTION_INFO['ip'],\
             self.CONNECTION_INFO['udpport']))

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
    def __init__(self, CONNECTION_INFO, gsi):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi

    def startedConnecting(self, connector):
        log.msg('Starting connection...')

    def buildProtocol(self, addr):
        log.msg('Building protocol...')
        self.resetDelay()
        return ClientProtocol(self.CONNECTION_INFO, self.gsi)

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection.  Reason: ', reason)
        ReconnectingClientFactory.clientConnectionLost(self,\
         connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionFailed(self,\
         connector, reason)


class Client():
    """
    This class starts the client by reading the configuration 
    parameters either from a file called config.ini or from the command line.

    :ivar CONNECTION_INFO:
        This variable contains the following data: username, password, slot_id, 
        connection (either 'serial' or 'udp'), serialport, baudrate, ip, port.
    :type CONNECTION_INFO:
        L{Dictionary}

    """
    # CONNECTION_INFO = {}

    # def __init__(self, argv, CONNECTION_INFO):
    #     log.startLogging(sys.stdout)

    #     if ('-h','') in opts:
    #         self.usage()
    #         return
    #     elif ('-f','') in opts:
    #         self.readFileConfig()
    #         self.createConnection()
    #     elif ('-g','') in opts:
    #         # self.readFileConfig()
    #         # ex = SatNetGUI()
    #         self.readCMDConfig(opts)
    #         self.createConnection()


    def __init__(self, CONNECTION_INFO):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.createConnection()

    def createConnection(self):
        gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo")
        reactor.connectSSL('localhost', 1234,\
         ClientReconnectFactory(self.CONNECTION_INFO, gsi),\
          ClientContextFactory())

    def readFileConfig(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read("config.ini")

        self.CONNECTION_INFO['username'] = config.get('User', 'username')
        self.CONNECTION_INFO['password'] = config.get('User', 'password')
        self.CONNECTION_INFO['slot_id'] = config.get('User', 'slot_id')        
        self.CONNECTION_INFO['connection'] = config.get('User', 'connection')        
        if self.CONNECTION_INFO['connection'] == 'serial':
            self.CONNECTION_INFO['serialport'] = config.get('Serial',\
             'serialport')
            self.CONNECTION_INFO['baudrate'] = config.get('Serial',\
             'baudrate')
        if self.CONNECTION_INFO['connection'] == 'udp':
            self.CONNECTION_INFO['ip'] = config.get('UDP', 'ip')
            self.CONNECTION_INFO['udpport'] = int(config.get('UDP',\
             'udpport'))
        self.paramValidation()

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
        print ("USAGE of client_amp.py\n"
                "Usage: python client_amp.py [-h] # Shows script help\n"
                "Usage: python client_amp.py [-f] # Load config from file\n"                
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
                "Example using file config: python client_amp.py -f -t 2\n"
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


class SatNetGUI(QtGui.QDialog):

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.initUI()

    def initUI(self):
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 12))
        self.resize(1300, 800)
        self.setWindowTitle("SATNet client - Universidade de Vigo") 

        # Control buttons.
        buttons = QtGui.QGroupBox(self)
        buttons.setLayout(QtGui.QHBoxLayout(buttons))

        # New connection.
        ButtonNew = QtGui.QPushButton("New connection", buttons)
        ButtonNew.setFixedWidth(145)
        ButtonNew.clicked.connect(self.NewConnection)
        # Close connection.
        ButtonCancel = QtGui.QPushButton("Close connection", buttons)
        ButtonCancel.setFixedWidth(145)
        ButtonCancel.clicked.connect(self.CloseConnection)

        buttons.layout().addWidget(ButtonNew)
        buttons.layout().addWidget(ButtonCancel)
        buttons.setTitle("Connection parameters")
        buttons.move(10, 10)

        # Parameters group.
        parameters = QtGui.QGroupBox(self)
        layout = QtGui.QFormLayout()
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

        parameters.setLayout(layout)
        parameters.setTitle("Connection parameters")
        parameters.move(10, 150)

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
        console.setFont(QtGui.QFont('SansSerif', 12))

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
                # elif opt == "-t":
                #     self.LabelSlotID.setText(arg)
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

    def NewConnection(self):
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
        else:
            self.CONNECTION_INFO['username'] = str(self.LabelUsername.text())
            self.CONNECTION_INFO['password'] = str(self.LabelPassword.text())
            self.CONNECTION_INFO['slot_id'] = int(self.LabelSlotID.text())
            self.CONNECTION_INFO['connection'] = str(self.LabelConnection.currentText())
            self.CONNECTION_INFO['serialport'] = str(self.LabelSerialPort.currentText())
            self.CONNECTION_INFO['baudrate'] = str(self.LabelBaudrate.text())
            self.CONNECTION_INFO['ip'] = self.LabelUDP.text()
            self.CONNECTION_INFO['udpport'] = self.LabelUDPPort.text()

        c = Client(self.CONNECTION_INFO)

    # To-do. Not closed properly.
    def CloseConnection(self):
        reactor.stop()
        self.close()

    def CheckConnection(self):
        Connection = str(self.LabelConnection.currentText())

        if Connection == 'serial':
            # from glob import glob
            # ports = glob('/dev/tty[A-Za-z]*')
            # self.LabelSerialPort.addItems(ports)
            self.LabelSerialPort.setEnabled(True)
            self.LabelBaudrate.setEnabled(True)
            self.LabelUDP.setEnabled(False)
            self.LabelUDPPort.setEnabled(False)
        elif Connection == 'udp':
            self.LabelSerialPort.setEnabled(False)
            self.LabelBaudrate.setEnabled(False)
            self.LabelUDP.setEnabled(True)
            self.LabelUDPPort.setEnabled(True)

    # def readCMDConfig(self, opts):


class XStream(QtCore.QObject):
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


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    myapp = SatNetGUI()
    myapp.show()

    from qtreactor import pyqt4reactor
    pyqt4reactor.install()

    from twisted.internet import reactor
    reactor.run()

    # sys.exit(app.exec_())
