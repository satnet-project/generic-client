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
from PyQt4 import QtGui

from twisted.python import log
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.amp import AMP
from twisted.cred.credentials import UsernamePassword
from twisted.internet.defer import inlineCallbacks

from protocol.ampauth.client import Login
from protocol.commands import *
from protocol.errors import *

from gs_interface import GroundStationInterface
import getpass, getopt, threading
import misc

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
            res = yield self.callRemote(Login, sUsername=self.CONNECTION_INFO['username'], sPassword=self.CONNECTION_INFO['password'])
            res = yield self.callRemote(StartRemote, iSlotId=self.CONNECTION_INFO['slot_id'])
        except Exception as e:            
            log.err(e)
            reactor.stop()

    def vNotifyMsg(self, sMsg):
        log.msg("(" + self.CONNECTION_INFO['username'] + ") --------- Notify Message ---------")
        log.msg(sMsg)
        if self.CONNECTION_INFO['connection'] == 'serial':        
            self.kissTNC.write(sMsg)
        elif self.CONNECTION_INFO['connection'] == 'udp':
            self.UDPSocket.sendto(sMsg, (self.CONNECTION_INFO['ip'], self.CONNECTION_INFO['udpport']))

        return {}
    NotifyMsg.responder(vNotifyMsg)

    def processFrame(self, frame):
        log.msg('Received frame: ' + frame)
        res = self.callRemote(SendMsg, sMsg=frame, iTimestamp=misc.get_utc_timestamp())
        log.msg(res)

    def vNotifyEvent(self, iEvent, sDetails):
        log.msg("(" + self.CONNECTION_INFO['username'] + ") --------- Notify Event ---------")
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
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


class Client():
    """
    This class starts the client by reading the configuration parameters either from
    a file called config.ini or from the command line.

    :ivar CONNECTION_INFO:
        This variable contains the following data: username, password, slot_id, 
        connection (either 'serial' or 'udp'), serialport, baudrate, ip, port.
    :type CONNECTION_INFO:
        L{Dictionary}

    """
    CONNECTION_INFO = {}

    def __init__(self, argv):
        log.startLogging(sys.stdout)

        try:
           opts, args = getopt.getopt(argv,"hfgu:p:t:c:s:b:i:u:",
            ["username=","password=","slot=","connection=","serialport=","baudrate=","ip=","udpport="])
        except getopt.GetoptError:
            log.msg('Incorrect script usage')
            self.usage()
            return
        if ('-h','') in opts:
            self.usage()
            return
        elif ('-f','') in opts:
            log.msg('entra')
            self.readFileConfig()
            self.createConnection()
        elif ('-g','') in opts:
            self.readFileConfig()
            ex = SatNetGUI()
        else:
            self.readCMDConfig(opts)
            self.createConnection()
        
        reactor.run()

    def createConnection(self):
        gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo")
        reactor.connectSSL('localhost', 1234, ClientReconnectFactory(self.CONNECTION_INFO, gsi), ClientContextFactory())

    def readCMDConfig(self, opts):
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

    def readFileConfig(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read("config.ini")

        self.CONNECTION_INFO['username'] = config.get('User', 'username')
        self.CONNECTION_INFO['password'] = config.get('User', 'password')
        self.CONNECTION_INFO['slot_id'] = config.get('User', 'slot_id')        
        self.CONNECTION_INFO['connection'] = config.get('User', 'connection')        
        if self.CONNECTION_INFO['connection'] == 'serial':
            self.CONNECTION_INFO['serialport'] = config.get('Serial', 'serialport')
            self.CONNECTION_INFO['baudrate'] = config.get('Serial', 'baudrate')
        if self.CONNECTION_INFO['connection'] == 'udp':
            self.CONNECTION_INFO['ip'] = config.get('UDP', 'ip')
            self.CONNECTION_INFO['udpport'] = int(config.get('UDP', 'udpport'))
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
                "Example for serial config: python client_amp.py -u crespo -p cre.spo -t 2 -c serial -s /dev/ttyS1 -b 115200\n"
                "Example for udp config: python client_amp.py -u crespo -p cre.spo -t 2 -c udp -i 127.0.0.1 -u 5001\n"
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


class SatNetGUI(QtGui.QWidget):
    
    def __init__(self):
        super(SatNetGUI, self).__init__()
        self.initUI()
        
    def initUI(self):
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        
        self.lName = QtGui.QLabel("Test", self)
        self.lName.move(20, 20)
        self.leTitle = QtGui.QLineEdit(self)
        self.leTitle.move(20, 40)
        #self.leTitle.textChanged.connect(func)

        self.btnNew = QtGui.QPushButton('Test BTN', self)
        self.btnNew.move(20, 80)
        #self.btnNew.clicked.connect(self.fdm.addEvent)

        self.btnStop = QtGui.QPushButton('Test2 BTN', self)
        self.btnStop.move(120, 80)


        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Icon')
        #self.setWindowIcon(QtGui.QIcon('web.png'))
        self.show()

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    from qtreactor import pyqt4reactor
    pyqt4reactor.install()
    from twisted.internet import reactor
    # sys.exit frozes the program. Possible solution in https://github.com/ghtdak/qtreactor/issues/1
    #sys.exit(app.exec_())
    c = Client(sys.argv[1:])
