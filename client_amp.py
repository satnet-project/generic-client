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

from ampauth.client import login
from commands import *

import serial, getpass, sys, getopt


class ClientProtocol(AMP):
    USERNAME = None
    PASSWORD = None
    SERIALPORT = None
    ser = None

    def user_login(self):

        d = login(self, UsernamePassword(self.USERNAME, self.PASSWORD))
        def connected(self, proto):
            proto.callRemote(StartRemote, iSlotId=1)
        d.addCallback(connected, self)
        def notConnected(failure):
            log.err("Error during connection")
            reactor.stop()
        d.addErrback(notConnected)
        def open_serial(self, proto):
            proto.ser = serial.Serial(proto.SERIALPORT, 19200, timeout=1)
            print proto.ser.name
        d.addCallback(open_serial, self)
        def serial_unavailable(failure):
            log.err("Serial port not available")
            reactor.stop()
        d.addErrback(serial_unavailable)
        return d

    def connectionLost(self, reason):
        log.err(reason)
        super(ClientProtocol, self).connectionLost(reason)

    def vNotifyMsg(self, sMsg):
        log.msg("(" + self.USERNAME + ") --------- Notify Message ---------")
        log.msg(sMsg)
        self.callRemote(EndRemote)                
        return {}
    NotifyMsg.responder(vNotifyMsg)

    def vNotifyEvent(self, iEvent, sDetails):
        log.msg("(" + self.USERNAME + ") --------- Notify Event ---------")
        if iEvent == NotifyEvent.SLOT_END:
            log.msg("Disconnection because the slot has ended")
        elif iEvent == NotifyEvent.REMOTE_DISCONNECTED:
            log.msg("Remote client has lost the connection")
        elif iEvent == NotifyEvent.END_REMOTE:
            log.msg("Disconnection because the remote client has been disconnected")
        elif iEvent == NotifyEvent.REMOTE_CONNECTED:
            log.msg("The remote client has just connected")

        return {}
    NotifyEvent.responder(vNotifyEvent)


class Client():    
    def __init__(self, argv):
        log.startLogging(sys.stdout)

        USERNAME = None
        PASSWORD = None
        SERIALPORT = None

        try:
           opts, args = getopt.getopt(argv,"hu:p:s:",["username=","password=","serialport="])
        except getopt.GetoptError:
            log.msg('Incorrect script usage')
            self.usage()
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                self.usage()
                sys.exit()
            elif opt in ("-u", "--username"):
                USERNAME = arg
            elif opt in ("-p", "--password"):
                PASSWORD = arg
            elif opt in ("-s", "--serialport"):
                SERIALPORT = arg

        if USERNAME is None:
            log.msg('Enter SATNET username: ')
            USERNAME = raw_input()
        if PASSWORD is None:
            log.msg('Enter', USERNAME,' password: ')
            PASSWORD = getpass.getpass()
        if SERIALPORT is None:
            log.msg('Select serial port: (e.g. /dev/ttyS1)')
            SERIALPORT = raw_input()

        #Load certificate to initialize a SSL connection
        cert = ssl.Certificate.loadPEM(open('key/public.pem').read())
        options = ssl.optionsForClientTLS(u'humsat.org', cert)

        # Create a protocol instance to connect with the server 
        factory = protocol.Factory.forProtocol(ClientProtocol)
        endpoint = endpoints.SSL4ClientEndpoint(reactor, 'localhost', 1234,
                                                options)
        d = endpoint.connect(factory)
        def connectionSuccessful(clientAMP, USERNAME, PASSWORD, SERIALPORT):
            self.proto = clientAMP
            clientAMP.USERNAME = USERNAME
            clientAMP.PASSWORD = PASSWORD
            clientAMP.SERIALPORT = SERIALPORT
            clientAMP.user_login()
            return clientAMP            
        d.addCallback(connectionSuccessful, USERNAME, PASSWORD, SERIALPORT)        
        def connectionError():
            log.err('Connection could not be established')
        d.addErrback(connectionError)            
        reactor.run()

    def usage(self):
        print "USAGE of client_amp.py"
        print "Usage: python [-h] client_amp.py #Shows script help"
        print "Usage: python [-u <username>] client_amp.py #Set SATNET username to login"
        print "Usage: python [-p <password>] client_amp.py #Set SATNET user password to login"
        print "Usage: python [-s <serialport>] client_amp.py #Set serial port to read data from"        
        print "Example: python -u crespo -p cre.spo -s /dev/ttyS1"        

if __name__ == '__main__':
    c = Client(sys.argv[1:])