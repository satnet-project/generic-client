# coding=utf-8
import unittest
import sys

from os import path
from PyQt4 import QtGui

from mock import Mock, MagicMock

from twisted.protocols.amp import AMP
from twisted.protocols.policies import TimeoutMixin
from twisted.test.proto_helpers import StringTransport
from twisted.internet import defer, reactor, ssl
from twisted.internet.protocol import Factory,Protocol, ServerFactory
from mock import patch

sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))
import misc
from gs_interface import GroundStationInterface
from client_amp import ClientProtocol, Client
from client_ui import  SatNetUI
from ampCommands import Login

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


class MockFactory(ServerFactory):

    pass


class MockServerProtocol(AMP, TimeoutMixin):

    def connectionMade(self):
        print "helou"

    def connectionLost(self, *a):
        self.factory.onConnectionLost.callback(self)

    def login(self, sUsername, sPassword):

        print "aloja"

        if sUsername in self.factory.active_protocols:
            log.msg('Client already logged in, renewing...')
        else:
            self.username = sUsername
            self.password = sPassword
            self.factory.active_protocols[sUsername] = None

        print '>>> @login: username = ' + str(
            sUsername
        ) + ', pwd = ' + str(sPassword)

        self.rpc = rpcrequests.SatnetRPC(sUsername, sPassword)
        self.factory.active_protocols[sUsername] = self

        log.msg('Connection made!, clients = ' + str(
            len(self.factory.active_protocols))
        )

        return {'bAuthenticated': True}

    Login.responder(login)


class MockServerFactory(ServerFactory):

    protocol = MockServerProtocol()


class TestConnectionProcessIntegrated(unittest.TestCase):

    app = QtGui.QApplication(sys.argv)

    def createSettingsFile(self):
        testFile = open(".settings", "w")
        testFile.write("[User]\n"
                       "username = test-sc-user\n"
                       "password = sgongarpass\n"
                       "slot_id = -1\n"
                       "connection = none\n"
                       "\n"
                       "[Serial]\n"
                       "serialport = /dev/ttyUSB0\n"
                       "baudrate = 500000\n"
                       "\n"
                       "[udp]\n"
                       "udpipreceive = 127.0.0.1\n"
                       "udpportreceive = 1234\n"
                       "udpipsend = 172.19.51.145\n"
                       "udpportsend = 57009\n"
                       "\n"
                       "[tcp]\n"
                       "tcpipreceive = 127.0.0.1\n"
                       "tcpportreceive = 4321\n"
                       "tcpipsend = 127.0.0.1\n"
                       "tcpportsend = 1234\n"
                       "\n"
                       "[server]\n"
                       "serverip = 172.19.51.133\n"
                       "serverport = 1234\n"
                       "\n"
                       "[Connection]\n"
                       "reconnection = no\n"
                       "parameters = yes\n"
                       "\n"
                       "[Client]\n"
                       "name = Universidade de Vigo\n"
                       "attempts = 10")
        testFile.close()

    def setUp(self):
        # Server stuff
        # self.serverDisconnected = defer.Deferred()
        # self.serverPort = self._listenServer(self.serverDisconnected)

        self._listenServer()
        # connected = defer.Deferred()


        self.createSettingsFile()

        self.correctFrame = ("00:82:a0:00:00:53:45:52:50:2d:42:30:91:1d:1b:03:" +
                             "8d:0b:5c:03:02:28:01:9c:01:ab:02:4c:02:98:01:da:" +
                             "02:40:00:00:00:10:0a:46:58:10:00:c4:9d:cb:a2:21:39")
        self.wrongFrame = 9

        # return connected

    def _listenServer(self):
        from twisted.internet import reactor
        sf = MockServerFactory()
        # sf.onConnectionLost = d
        sf.protocol = MockServerProtocol()

        # cert = ssl.PrivateCertificate.loadPEM(open('../key/server.pem').read())

        return reactor.listenSSL(1234, sf, contextFactory=ssl.DefaultOpenSSLContextFactory('../key/server.pem',
                                                                                           '../key/public.pem'))

    def teardrown(self):
        d = defer.maybeDeferred(self.serverPort.stopListening)
        self.clientConnection.disconnect()
        return defer.gatherResults([d, self.clientDisconnected, self.serverDisconnected])

    """
    @patch.object(SatNetUI, 'initUI', return_value=True)
    @patch.object(SatNetUI, 'initButtons', return_value=True)
    @patch.object(SatNetUI, 'initFields', return_value=True)
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(SatNetUI, 'initConfiguration', return_value=True)
    @patch.object(SatNetUI, 'setArguments', return_value=True)
    @patch.object(SatNetUI, 'closeEvent', return_value=True)
    """
    """
    def test_loginRightUsernameRightPasswordRightConnection(self, initUI, initButtons, initFields, setParameters,
                                                            initLogo, initConfiguration, setArguments, closeEvent,
                                                            connectionMade, createconnection, NewConnection):
    """

    @patch.object(SatNetUI, 'initButtons', return_value=True)
    def test_blabla(self, initButtons):

        argumentsdict = misc.get_data_local_file('.settings')

        testUI = SatNetUI(argumentsdict)

        # testUI.gsi = GroundStationInterface(self.CONNECTION_INFO, 'Vigo', ClientProtocol)
        testUI.LabelUsername.setText('username')
        testUI.LabelPassword.setText('password')
        testUI.LabelConnection.addItem('udp')
        index = testUI.LabelConnection.findText('udp')
        testUI.LabelConnection.setCurrentIndex(index)

        testUI.ButtonNew = Mock()
        testUI.ButtonNew.setEnabled = MagicMock(return_value=True)
        testUI.ButtonCancel = Mock()
        testUI.ButtonCancel.setEnabled = MagicMock(return_value=True)
        testUI.LoadDefaultSettings = Mock()
        testUI.LoadDefaultSettings.setEnabled = MagicMock(return_value=True)
        testUI.AutomaticReconnection = Mock()
        testUI.AutomaticReconnection.setEnabled = MagicMock(return_value=True)

        print testUI.NewConnection(test=True)

        # self.assertTrue(callRemote(Login, sUsername='nombre', sPassword='pass'))
