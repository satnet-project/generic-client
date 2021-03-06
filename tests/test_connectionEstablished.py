# coding=utf-8
import os
import sys

# Dependencies for the tests
from mock import patch
from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransportWithDisconnection
from twisted.internet.protocol import Factory

from twisted.protocols.amp import AMP, BoxDispatcher

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))

import client_amp
from gs_interface import GroundStationInterface

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


# TODO Complete description
class MockFactory(Factory):
    """

    """
    pass


class TestClientProtocolConnectionMade(TestCase):
    def setUp(self):
        CONNECTION_INFO = {'username': 'satnet_admin', 'password': 'pass',
                           'udpipsend': '172.19.51.145','baudrate': '500000',
                           'name': 'Universidade de Vigo', 'parameters': 'yes',
                           'tcpportsend': '1234', 'tcpipsend': '127.0.0.1',
                           'udpipreceive': '127.0.0.1', 'attempts': '10',
                           'serverip': '172.19.51.143',
                           'serialport': '/dev/ttyUSB0','tcpportreceive': 4321,
                           'connection': 'udp', 'udpportreceive': 57008,
                           'serverport': 25345, 'reconnection': 'no',
                           'udpportsend': '57009',
                           'tcpipreceive': '127.0.0.1'}

        GS = 'VigoTest'

        gsi = GroundStationInterface(CONNECTION_INFO, GS, AMP)
        threads = object

        self.sp = client_amp.ClientProtocol(CONNECTION_INFO, gsi, threads)
        self.sp.factory = MockFactory()
        self.transport = StringTransportWithDisconnection()

        self.transport.protocol = self.sp

    def tearDown(self):
        pass

    # TODO Complete description
    def test_clientconnectionEstablished(self):
        """

        @return:
        """
        self.sp.makeConnection(self.transport)
        return self.assertTrue(self.transport.connected)

    # TODO Complete description
    @patch.object(client_amp.ClientProtocol, 'connectionMade')
    def test_connectionMadeAtClientProtocolSideCalled(self, connnectionMade):
        """

        @param connnectionMade:
        @return:
        """
        self.sp.makeConnection(self.transport)
        return self.assertTrue(self.sp.connectionMade.called)

    # TODO Complete description
    @patch.object(client_amp.ClientProtocol, 'user_login')
    @patch.object(GroundStationInterface, 'connectProtocol')
    def test_connectionMethodsCalled(self, user_login, connectProtocol):
        """

        @param user_login:
        @param connectProtocol:
        @return:
        """
        self.sp.makeConnection(self.transport)
        return self.assertTrue(connectProtocol.called),\
               self.assertTrue(user_login.called)


