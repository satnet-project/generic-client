# coding=utf-8
import unittest
import sys

from os import path
from PyQt4 import QtGui

from mock import Mock, MagicMock

from twisted.python import log
from twisted.protocols.amp import AMP
from twisted.protocols.policies import TimeoutMixin
from twisted.test.proto_helpers import StringTransport
from twisted.internet import defer, reactor, ssl
from twisted.internet.protocol import Factory,Protocol, ServerFactory, ClientFactory
from mock import patch
from twisted.internet import defer, protocol
from twisted.trial import unittest
from twisted.protocols.amp import AMP

sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))
import misc
from gs_interface import GroundStationInterface
from client_amp import ClientProtocol, Client, ClientReconnectFactory, CtxFactory
from client_ui import  SatNetUI
from threads import Threads
from ampCommands import Login


class MockServerFactory(Factory):
    active_protocols = {}
    active_connections = {}

class ServerProtocol(AMP):
    def connectionLost(self, *a):
        self.factory.onConnectionLost.callback(self)

    def login(self, sUsername, sPassword):

        if sUsername in self.factory.active_protocols:
            log.msg('Client already logged in, renewing...')
        else:
            self.username = sUsername
            self.password = sPassword
            self.factory.active_protocols[sUsername] = None

        # self.rpc = rpcrequests.SatnetRPC(sUsername, sPassword)
        self.factory.active_protocols[sUsername] = self

        log.msg('Connection made!, clients = ' + str(
            len(self.factory.active_protocols))
        )

        return {'bAuthenticated': True}

    Login.responder(login)


class ClientProtocol(AMP):
    def connectionMade(self):
        self.factory.protoInstance = self
        self.factory.onConnectionMade.callback(self)

    def connectionLost(self, *a):
        self.factory.onConnectionLost.callback(self)

class TestConnectionProcessIntegrated(unittest.TestCase):
    def setUp(self):
        self.serverDisconnected = defer.Deferred()
        self.serverPort = self._listenServer(self.serverDisconnected)
        connected = defer.Deferred()
        self.clientDisconnected = defer.Deferred()
        self.clientConnection = self._connectClient(connected, self.clientDisconnected)
        return connected

    def _listenServer(self, d):
        from twisted.internet import reactor
        f = MockServerFactory()
        f.onConnectionLost = d
        f.protocol = ServerProtocol
        return reactor.listenSSL(1234, f, contextFactory=ssl.DefaultOpenSSLContextFactory('../key/server.pem',
                                                                                           '../key/public.pem'))

    def _connectClient(self, d1, d2):
        from twisted.internet import reactor
        self.factory = protocol.ClientFactory()
        self.factory.protocol = ClientProtocol
        self.factory.onConnectionMade = d1
        self.factory.onConnectionLost = d2
        return reactor.connectSSL('127.0.0.1', 1234, self.factory, CtxFactory())

    def tearDown(self):
        d = defer.maybeDeferred(self.serverPort.stopListening)
        self.clientConnection.disconnect()
        return defer.gatherResults([d, self.clientDisconnected, self.serverDisconnected])

    def test_loginRightUsernameRightPasswordRightConnection(self):
        d = self.factory.protoInstance.callRemote(Login, sUsername='sgongar', sPassword='sgongarpass')
        d.addCallback(lambda res : self.assertTrue(res['bAuthenticated']))
        return d
