# coding=utf-8
import sys
import os
import unittest
import mock

from twisted.python import log
from unittest import TestCase

from mock import Mock, MagicMock

from twisted.internet import defer, protocol, reactor, ssl
from twisted.internet.error import CannotListenError
from twisted.internet.protocol import Factory
from twisted.protocols.amp import AMP, Command, Integer, Boolean, String
from twisted.python import log

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from gs_interface import GroundStationInterface
from errors import WrongFormatNotification, SlotErrorNotification
from client_amp import ClientProtocol, CtxFactory, ClientReconnectFactory, NotifyMsg
import misc

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../protocol")))
from server_amp import SATNETServer
# from rpcrequests import Satnet_RPC

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../protocol/ampauth")))
# from server import CredReceiver, CredAMPServerFactory
# from errors import BadCredentials


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




class SendMsg(Command):
    
    arguments = [('sMsg', String()),
                 ('iTimestamp', Integer())]
    response = [('bResult', Boolean())]
    errors = {
        SlotErrorNotification: 'SLOT_ERROR_NOTIFICATION'}


class SATNETServer(protocol.Protocol):

    factory = None
    sUsername = ""
    credProto = None
    bGSuser = None
    slot = None
    
    def vSendMsg(self, sMsg, iTimestamp):

        # For tests only, where can I get the current channel?
        slot_id = 2
        slot = {'state': 'RESERVED',\
         'gs_channel': 'groundstation_channel',\
          'sc_channel': 'spacecraft_channel',\
           'starting_time': 1576836800, 'ending_time': 1677850000 }

        log.msg("(" + self.sUsername + ") --------- Send Message ---------")
        # If the client haven't started a connection via StartRemote command...
        # TODO. Never enters because the clients are in active_protocols as 
        # soon as they log in

        if self.sUsername not in self.factory.active_connections['localUsr']:
        # if self.sUsername not in self.factory.active_connections:
            log.msg('Connection not available. Call StartRemote command first')
            raise SlotErrorNotification(
                'Connection not available. Call StartRemote command first.')
        # ... if the SC operator is not connected, sent messages will be saved
        # as passive messages...
        elif self.factory.active_connections['localUsr'] == False:
            return {'bResult': False}
            
            if self.bGSuser == True:
                PassiveMessage = Satnet_StorePassiveMessage(groundstation_id =\
                 'groundstation_id', timestamp = 'timestamp', doppler_shift =\
                  'doppler_shift', message = sMsg, debug = True)

                log.msg('Message saved on server')

                # ... if the GS operator is not connected, the remote SC client 
                # will be notified to wait for the GS to connect...
            elif self.bGSuser == False:
                self.callRemote(NotifyEvent,\
                 iEvent=NotifyEvent.REMOTE_DISCONNECTED, sDetails=None)
                return {'bResult': False}
                # ... else, send the message to the remote and store it in the DB
        else:
            self.callRemote(NotifyMsg, sMsg="Protocol has received the message")

            gs_channel = slot['gs_channel']
            sc_channel = slot['sc_channel']

            log.msg("Saved message")
            
            slot_id = 2
            upwards = True
            forwarded = True
            timestamp = 1677850000

            Satnet_StoreMessage = mock.Mock()

            Message = Satnet_StoreMessage(slot_id, upwards, forwarded,\
             timestamp, sMsg, debug = True)

            return {'bResult': True}

    SendMsg.responder(vSendMsg)



class TestServerToClient(unittest.TestCase):
    """
    Testing for one single client connection
    To-do. Test timeout
    """

    def mock_callremote_true(self, NotifyMsg, sMsg):

        return True

    def mock_callremote(self, NotifyMsg, sMsg):

        CONNECTION_INFO = {'username':'s.gongoragarcia@gmail.com',
         'connection':'serial'}
        gsi = object

        ClientProtocol(CONNECTION_INFO, gsi).vNotifyMsg(sMsg)

    def mock_processframe(self, frame):
        CONNECTION_INFO = {}
        gsi = object
        clientprotocol = ClientProtocol(CONNECTION_INFO, gsi)
        # Mock callremote
        clientprotocol.callRemote = mock.MagicMock(
            side_effect=self.mock_callremote)
        clientprotocol._processframe(frame)

    def mockLoginMethod(self, username, password):
        return {'bAuthenticated': True}

    def setUp(self):
        log.startLogging(sys.stdout)
        log.msg(">>>>>>>>>>>>>>>>>>>>> Running tests")
        log.msg("")

        self.serverDisconnected = defer.Deferred()
        self.serverPort = self._listenServer(self.serverDisconnected)
        self.connected = defer.Deferred()
        self.clientDisconnected = defer.Deferred()
        self.clientConnection = self._connectClient(self.connected,
                                                    self.clientDisconnected)
        return self.connected

    def _listenServer(self, d):
        try:
            CredAMPServerFactory = mock.Mock()
            CredReceiver = mock.Mock()

            self.pf = CredAMPServerFactory()
            self.pf.protocol = CredReceiver()
            self.pf.protocol.login = MagicMock(
                side_effect=self.mockLoginMethod)
            self.pf.onConnectionLost = d
            cert = ssl.PrivateCertificate.loadPEM(
                open('key/server.pem').read())
            return reactor.listenSSL(1234, self.pf, cert.options())
        except CannotListenError:
            log.msg("Server already initialized")

    def _connectClient(self, d1, d2):
        self.factory = protocol.ClientFactory.forProtocol(ClientProtocol) 
        log.msg(self.factory)

        self.factory.onConnectionMade = d1
        self.factory.onConnectionLost = d2

        cert = ssl.Certificate.loadPEM(open('key/public.pem').read())
        options = ssl.optionsForClientTLS(u'example.humsat.org', cert)
        return reactor.connectSSL("localhost", 1234, self.factory, options)

    def tearDown(self):
        try:
            d = defer.maybeDeferred(self.serverPort.stopListening)
            self.clientConnection.disconnect()
            return defer.gatherResults([d, self.clientDisconnected, 
                                        self.serverDisconnected])
        except AttributeError:
            self.clientConnection.disconnect()
            return defer.gatherResults([self.clientDisconnected,
                                         self.serverDisconnected])            

    """
    Send a correct frame with connection
    """
    def test_AMPPresentCorrectFrame(self):
        log.msg(">>>>>>>>>>>>>>>>>>>>> Running AMPpresentCorrectFrame test")
        frame = 'Frame'

        protocol = SATNETServer()
        protocol.factory = mock.Mock()
        protocol.factory.active_connections = {'localUsr':'s.gongoragarcia@gmail.com'}
        protocol.sUsername = 's.gongoragarcia@gmail.com'
        protocol.callRemote = mock.MagicMock(side_effect=self.mock_callremote)

        protocol.vSendMsg(sMsg='hola', iTimestamp=misc.get_utc_timestamp())


if __name__ == '__main__':
    unittest.main()   