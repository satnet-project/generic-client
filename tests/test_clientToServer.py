# coding=utf-8
"""
   Copyright 2015 Samuel Góngora García

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


import sys
import os
import unittest
import mock
import time

from twisted.python import log
from unittest import TestCase

from mock import Mock, MagicMock

from twisted.internet import defer, protocol, reactor, ssl
from twisted.internet.error import CannotListenError
from twisted.internet.protocol import Factory
from twisted.protocols.amp import AMP, Command, Integer, Boolean, String
from twisted.python import log
from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from gs_interface import GroundStationInterface
from errors import WrongFormatNotification, SlotErrorNotification
from client_amp import ClientProtocol, CtxFactory, ClientReconnectFactory
import misc


class SendMsg(Command):
    
    arguments = [('sMsg', String()),
                 ('iTimestamp', Integer())]
    response = [('bResult', Boolean())]
    errors = {
        SlotErrorNotification: 'SLOT_ERROR_NOTIFICATION'}


"""
Testing for one single client connection
To-do. Test timeout
"""
class TestClientToServer(unittest.TestCase):

    def mock_callremote(self, SendMsg, sMsg, iTimestamp):
        return True
        # protocol = SATNETServer()
        # protocol.factory = mock.Mock()
        # protocol.factory.active_connections = {'localUsr':'s.gongoragarcia@gmail.com'}
        # protocol.sUsername = 's.gongoragarcia@gmail.com'
        # protocol.callRemote = mock.MagicMock(side_effect=self.mock_callremote_true)

        # protocol.vSendMsg(sMsg='hola', iTimestamp=misc.get_utc_timestamp())

    def mock_processframe(self, frame):
        CONNECTION_INFO = {}
        gsi = object
        
        clientprotocol = ClientProtocol(CONNECTION_INFO, gsi)
        # Mock callremote
        clientprotocol.callRemote = mock.MagicMock(side_effect=self.mock_callremote)
        clientprotocol._processframe(frame)

    def mockLoginMethod(self, username, password):
        return {'bAuthenticated': True}

    def setUp(self):
        log.startLogging(sys.stdout)
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> Running tests")
        log.msg("")

        self.serverDisconnected = defer.Deferred()
        self.serverPort = self._listenServer(self.serverDisconnected)
        self.connected = defer.Deferred()
        self.clientDisconnected = defer.Deferred()
        self.clientConnection = self._connectClient(self.connected,\
         self.clientDisconnected)
        return self.connected

    def _listenServer(self, d):
        try:
            CredAMPServerFactory = mock.Mock()
            CredReceiver = mock.Mock()

            self.pf = CredAMPServerFactory()
            self.pf.protocol = CredReceiver()
            self.pf.protocol.login = MagicMock(side_effect=self.mockLoginMethod)
            self.pf.onConnectionLost = d
            cert = ssl.PrivateCertificate.loadPEM(
                open('key/server.pem').read())
            return reactor.listenSSL(1234, self.pf, cert.options())
        except CannotListenError:
            log.msg("Server already initialized")

    def _connectClient(self, d1, d2):
        self.factory = protocol.ClientFactory.forProtocol(ClientProtocol)
        
        self.factory.onConnectionMade = d1
        self.factory.onConnectionLost = d2

        cert = ssl.Certificate.loadPEM(open('key/public.pem').read())
        
        options = ssl.optionsForClientTLS(u'example.humsat.org', cert)
        return reactor.connectSSL("localhost", 1234, self.factory, options)

    def tearDown(self):
        try:
            d = defer.maybeDeferred(self.serverPort.stopListening)
            self.clientConnection.disconnect()
            return defer.gatherResults([d, self.clientDisconnected,\
             self.serverDisconnected])
        except AttributeError:
            self.clientConnection.disconnect()
            return defer.gatherResults([self.clientDisconnected,\
             self.serverDisconnected])            

    """
    Send a correct frame without connection
    """
    def test_AMPnotPresentCorrectFrame(self):
 
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPnotPresentCorrectFrame test")

        frame = 'Frame'
        CONNECTION_INFO = {}
        GS = 'Vigo'
        self.amp = None

        gsi = GroundStationInterface(CONNECTION_INFO, GS, self.amp)
        gsi._manageFrame(frame)

        assert os.path.exists("ESEO-" + GS + "-" +\
         time.strftime("%Y.%m.%d") + ".csv") == 1
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMP not present - Local file created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPnotPresentCorrectFrame test OK")

    """
    Send an incorrect frame without connection
    """
    def test_AMPnotPresentIncorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPnotPresentIncorrectFrame test")

        frame = 1234
        CONNECTION_INFO = {}
        GS = 'Vigo'
        self.amp = None

        gsi = GroundStationInterface(CONNECTION_INFO, GS, self.amp)

        self.assertRaisesRegexp(WrongFormatNotification, "Bad format frame",\
          lambda: gsi._manageFrame(frame))
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMP not present - Local file not created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPnotPresentIncorrectFrame test OK")

    """
    Send an incorrect frame with connection
    """
    def test_AMPPresentIncorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPPresentIncorrectFrame")

        frame = 1234
        CONNECTION_INFO = {}
        GS = 'Vigo'
        self.amp = mock.Mock()

        gsi = GroundStationInterface(CONNECTION_INFO, GS, self.amp)

        self.assertRaisesRegexp(Exception, "Bad format frame",\
          lambda: gsi._manageFrame(frame))
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Error - Local file not created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPPresentIncorrectFrame test OK")

    """
    Send a correct frame with connection
    """
    def test_AMPPresentCorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPpresentCorrectFrame test")

        frame = 'Frame'
        CONNECTION_INFO = {}
        GS = 'Vigo'

        self.amp = AMP()
        self.amp._processframe = mock.MagicMock(side_effect=self.mock_processframe)
        gsi = GroundStationInterface(CONNECTION_INFO, GS, self.amp)._manageFrame(frame)


if __name__ == '__main__':
    unittest.main()   