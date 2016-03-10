# coding=utf-8
import unittest
import sys

from os import path

from mock import Mock, MagicMock, patch

from twisted.python import log
from twisted.protocols.amp import AMP
from twisted.protocols.policies import TimeoutMixin
from twisted.test.proto_helpers import StringTransport
from twisted.internet import defer, reactor, ssl
from twisted.internet.protocol import Factory,Protocol, ServerFactory, ClientFactory
from twisted.internet import defer, protocol
from twisted.trial import unittest
from twisted.protocols.amp import AMP

sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))
import misc
from gs_interface import GroundStationInterface
from client_amp import Client, ClientReconnectFactory, CtxFactory
from client_ui import  SatNetUI
from threads import Threads
from ampCommands import Login, StartRemote
from errors import SlotErrorNotification


class MockServerFactory(Factory):
    active_protocols = {'xabi':'xabiprotocol'}
    active_connections = {}


class ServerProtocol(AMP):
    def connectionLost(self, *a):
        self.factory.onConnectionLost.callback(self)

    def login(self, sUsername, sPassword):

        if sUsername in self.factory.active_protocols:
            log.msg('Client already logged in, renewing...')
            # What's the point of logging an user already logged?
            return {'bAuthenticated': False}
        else:
            self.username = sUsername
            self.password = sPassword
            self.factory.active_protocols[sUsername] = None

        # To-do. Mock function call.
        # self.rpc = rpcrequests.SatnetRPC(sUsername, sPassword)
        self.rpc = Mock
        self.rpc.testing = MagicMock(return_value=True)

        self.factory.active_protocols[sUsername] = self

        log.msg('Connection made!, clients = ' + str(
            len(self.factory.active_protocols))
        )

        return {'bAuthenticated': True}

    Login.responder(login)

    def decode_user(self, slot):
        """Decodes the information of the client
        :param slot:
        :return:
        """
        if not slot:
            err_msg = 'No operational slots for the user'
            log.err(err_msg)
            raise SlotErrorNotification(err_msg)

        gs_user = slot['gs_username']
        sc_user = slot['sc_username']

        client_a = sc_user
        client_b = gs_user
        if gs_user == self.username:
            client_a = gs_user
            client_b = sc_user

        return gs_user, sc_user, client_a, client_b

    def check_slot_ownership(self, gs_user, sc_user):
        """Checks if this slot has not been assigned to this user
        :param gs_user: Username of the groundstation user
        :param sc_user: Username of the spacecraft user
        """

        # print '>>> gs_user = ' + str(gs_user)
        # print '>>> sc_user = ' + str(sc_user)
        # print '>>> self.username = ' + str(self.username)

        if gs_user != self.username and sc_user != self.username:
            err_msg = 'This slot has not been assigned to this user'
            log.err(err_msg)
            raise SlotErrorNotification(err_msg)

    def start_remote_user(self):
        """Start Remote
        This function implements the checks to be executed after a START REMOTE
        command coming from a user.
        """

        rpcrequests = Mock()
        rpcrequests.RPC_TEST_USER_GS = 'test-user-gs'
        rpcrequests.RPC_TEST_USER_SC = 'test-user-sc'

        if self.rpc.testing:
            slot = {
                'id': -1,
                'gs_username': rpcrequests.RPC_TEST_USER_GS,
                'sc_username': rpcrequests.RPC_TEST_USER_SC,
                'ending_time': None
            }
        else:
            slot = self.rpc.get_next_slot(self.username)

        gs_user, sc_user, client_a, client_c = self.decode_user(slot)
        self.check_slot_ownership(gs_user, sc_user)

        return slot, gs_user, sc_user, client_a, client_c

    def i_start_remote(self):
        """RPC Handler
        This function processes the remote request through the StartRemote AMP
        command.
        FIXME iSlotId is no longer necessary...
        :param iSlotId:
        """
        log.msg('(' + self.username + ') --------- Start Remote ---------')
        slot, gs_user, sc_user, client_a, client_c = self.start_remote_user()
        return self.create_connection(
            slot['ending_time'], slot['id'], client_a, client_c
        )

    StartRemote.responder(i_start_remote)


class ClientProtocol(AMP):
    # TODO Complete description
    def connectionMade(self):
        """ Override connection made method

        @return:
        """
        self.factory.protoInstance = self
        self.factory.onConnectionMade.callback(self)

    # TODO Complete description
    def connectionLost(self, *a):
        """

        @param a:
        @return:
        """
        self.factory.onConnectionLost.callback(self)


class TestConnectionProcessIntegrated(unittest.TestCase):

    def createSettingsFile(self):
        """

        @return:
        """
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
                       "serverport = 25345\n"
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
        self.CONNECTION_INFO = {'username': 'satnet_admin', 'password': 'pass',
                                'udpipsend': '172.19.51.145',
                                'baudrate': '500000',
                                'name': 'Universidade de Vigo',
                                'parameters': 'yes',
                                'tcpportsend': '1234',
                                'tcpipsend': '127.0.0.1',
                                'udpipreceive': '127.0.0.1',
                                'attempts': '10', 'serverip': '172.19.51.143',
                                'serialport': '/dev/ttyUSB0',
                                'tcpportreceive': 4321, 'connection': 'udp',
                                'udpportreceive': 57008, 'serverport': 25345,
                                'reconnection': 'no', 'udpportsend': '57009',
                                'tcpipreceive': '127.0.0.1'}
        self.gsi = GroundStationInterface(self.CONNECTION_INFO, 'Vigo', AMP)
        self.threads = Threads(self.CONNECTION_INFO, self.gsi)

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

        return reactor.listenSSL(1234, f,
                                 contextFactory=ssl.DefaultOpenSSLContextFactory('../../key/server.pem',
                                                                                          '../../key/public.pem'))

    def _connectClient(self, d1, d2):
        from twisted.internet import reactor
        # self.factory = ClientReconnectFactory(self.CONNECTION_INFO, self.gsi, self.threads)
        self.factory = protocol.ClientFactory()
        self.factory.protocol = ClientProtocol
        # self.factory.protocol = ClientProtocol(self.CONNECTION_INFO, self.gsi, self.threads)
        self.factory.onConnectionMade = d1
        self.factory.onConnectionLost = d2
        return reactor.connectSSL('127.0.0.1', 1234, self.factory, CtxFactory())

    def tearDown(self):
        d = defer.maybeDeferred(self.serverPort.stopListening)
        self.clientConnection.disconnect()
        return defer.gatherResults([d, self.clientDisconnected,
                                    self.serverDisconnected])

    # FIXME Fix test and complete description
    def _test_loginRightUsernameRightPasswordRightConnection(self):
        """

        @return:
        """
        d = self.factory.protoInstance.callRemote(Login, sUsername='sgongar',
                                                  sPassword='sgongarpass')
        d.addCallback(lambda res : self.assertTrue(res['bAuthenticated']))
        return d

    # FIXME Fix test and complete description
    def _test_loginWrongUsernameRightPasswordRightConnection(self):
        """

        @return:
        """
        d = self.factory.protoInstance.callRemote(Login, sUsername='xabi',
                                                  sPassword='xabipass')
        d.addCallback(lambda res : self.assertFalse(res['bAuthenticated']))
        return d

    # TODO Complete description
    def test_wrongUsernamestartRemoteFailed(self):
        """

        @return:
        """
        d = self.factory.protoInstance.callRemote(Login, sUsername='sgongar',
                                                  sPassword='sgongarpass')
        d.addCallback(lambda l : self.factory.protoInstance.callRemote(StartRemote))

        def checkError(result):
            self.assertEqual(result.message,
                             'This slot has not been assigned to this user')
        return self.assertFailure(d, SlotErrorNotification).addCallback(checkError)
