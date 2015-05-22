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

from twisted.python import log
from twisted.internet import reactor, ssl, defer, protocol, endpoints
from twisted.internet.protocol import ClientCreator
from twisted.internet.error import ReactorNotRunning
from twisted.protocols.amp import AMP
from twisted.cred.credentials import UsernamePassword

from protocol.ampauth.client import login
from protocol.commands import *
from protocol.errors import *

import getpass, getopt, threading
import misc

class ClientProtocol(AMP):

    CONNECTION_INFO = {}
    kissTNC = None
    UDPSocket = None
    thread = None

    def user_login(self):
        d = login(self, UsernamePassword(self.CONNECTION_INFO['username'], self.CONNECTION_INFO['password']))
        def connected(result):
            return self.callRemote(StartRemote, iSlotId=self.CONNECTION_INFO['slot_id'])
        d.addCallback(connected)
        def notConnected(failure):
            return failure
        d.addErrback(notConnected)
        def open_serial(result):
            self.kissTNC = kiss.KISS(self.CONNECTION_INFO['serialport'], self.CONNECTION_INFO['baudrate'])
            self.kissTNC.start()  # inits the TNC, optionally passes KISS config flags.
            self.thread = threading.Thread(target=self.kissTNC.read, args=(self.frameFromSerialport,))
            self.thread.daemon = True # This thread will be close if the reactor stops
            self.thread.start()
        def open_socket(result):
            self.UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            self.UDPSocket.bind((self.CONNECTION_INFO['ip'], self.CONNECTION_INFO['udpport']))
            self.thread = threading.Thread(target=self.frameFromUDPSocket)
            self.thread.daemon = True # This thread will be close if the reactor stops
            self.thread.start()

        if self.CONNECTION_INFO['connection'] == 'serial':
            import kiss
            d.addCallback(open_serial)
        elif self.CONNECTION_INFO['connection'] == 'udp':
            import socket
            d.addCallback(open_socket)            

        def error_handlers(failure):
            if failure.type == OSError:
                log.err("Is the TNC connected or the serial port correct?")
            log.err(failure.type)
            reactor.stop()
        d.addErrback(error_handlers)
        return d

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

    def frameFromSerialport(self, frame):
        log.msg("--------- Message from Serial port ---------")
        processFrame(frame)

    def frameFromUDPSocket(self):
        log.msg("--------- Message from UDP socket ---------")        
        while True:
            frame, addr = self.UDPSocket.recvfrom(1024) # buffer size is 1024 bytes
            processFrame(frame)

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


class Client():

    ###
    # CONNECTION_INFO contains the following data:
    #   -  username, password, slot_id, connection
    #   -  (serial connection) serialport, baudrate
    #   -  (udp connection) ip, port
    ###
    CONNECTION_INFO = {}

    def __init__(self, argv):
        log.startLogging(sys.stdout)

        try:
           opts, args = getopt.getopt(argv,"hfu:p:t:c:s:b:i:u:",
            ["username=","password=","slot=","connection=","serialport=","baudrate=","ip=","udpport="])
        except getopt.GetoptError:
            log.msg('Incorrect script usage')
            self.usage()
            return
        if ('-h','') in opts:
            self.usage()
            return
        elif ('-f','') in opts:
            self.readFileConfig(opts)
        else:
            self.readCMDConfig(opts)

        self.startConnectionEP()
        reactor.run()

    def startConnectionEP(self):
        # Reconnections must be implemented here!
        
        #Load certificate to initialize a SSL connection
        cert = ssl.Certificate.loadPEM(open('../protocol/key/public.pem').read())
        options = ssl.optionsForClientTLS(u'example.humsat.org', cert)        
        factory = protocol.Factory.forProtocol(ClientProtocol)
        endpoint = endpoints.SSL4ClientEndpoint(reactor, 'localhost', 1234, options)
        d = endpoint.connect(factory)
        def connectionSuccessful(clientAMP):
            clientAMP.CONNECTION_INFO = self.CONNECTION_INFO
            clientAMP.user_login()
            return clientAMP
        d.addCallback(connectionSuccessful)        
        def connectionError(error):
            log.err('Connection could not be established')
            log.err(error)
        d.addErrback(connectionError)

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

        if 'username' not in self.CONNECTION_INFO:
            log.msg('Enter SATNET username: ')
            self.CONNECTION_INFO['username']  = raw_input()
        if 'password' not in self.CONNECTION_INFO:
            log.msg('Enter', self.CONNECTION_INFO['username'],' password: ')
            self.CONNECTION_INFO['password']  = getpass.getpass()
        if self.CONNECTION_INFO['connection'] == 'serial':
            log.msg('Using a serial interface with the GS')
            if 'serialport' not in self.CONNECTION_INFO or 'baudrate' not in self.CONNECTION_INFO:
                log.msg('Missing some client configurations (serialport [-s] or baudrate [-b])')
                return
        if self.CONNECTION_INFO['connection'] == 'udp':
            log.msg('Using an UDP interface with the GS')
            if 'ip' not in self.CONNECTION_INFO or 'udpport' not in self.CONNECTION_INFO:
                log.msg('Missing some client configurations (ip [-i] or udpport [-u])')
                return

    def readFileConfig(self, opts):
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

if __name__ == '__main__':
    c = Client(sys.argv[1:])