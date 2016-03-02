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


class MockFactory(Factory):
    pass


class TestClientProtocolConnectionDown(TestCase):
    def setUp(self):
        CONNECTION_INFO = {'username': 'satnet_admin', 'password': 'pass', 'udpipsend': '172.19.51.145',
                           'baudrate': '500000', 'name': 'Universidade de Vigo', 'parameters': 'yes',
                           'tcpportsend': '1234', 'tcpipsend': '127.0.0.1', 'udpipreceive': '127.0.0.1',
                           'attempts': '10', 'serverip': '172.19.51.143', 'serialport': '/dev/ttyUSB0',
                           'tcpportreceive': 4321, 'connection': 'udp', 'udpportreceive': 57008,
                           'serverport': 25345, 'reconnection': 'no', 'udpportsend': '57009',
                           'tcpipreceive': '127.0.0.1'}

        GS = 'VigoTest'

        gsi = GroundStationInterface(CONNECTION_INFO, GS, AMP)
        threads = object

        self.sp = client_amp.ClientProtocol(CONNECTION_INFO, gsi, threads)
        self.sp.factory = MockFactory()
        self.transport = StringTransportWithDisconnection()
        self.sp.makeConnection(self.transport)

        self.transport.protocol = self.sp

        self.correctFrame = ("00:82:a0:00:00:53:45:52:50:2d:42:30:91:1d:1b:03:" +
                             "8d:0b:5c:03:02:28:01:9c:01:ab:02:4c:02:98:01:da:" +
                             "02:40:00:00:00:10:0a:46:58:10:00:c4:9d:cb:a2:21:39")

        self.wrongFrame = 9

    def tearDown(self):
        pass

    def test_clientconnectionLost(self):
        self.transport.loseConnection()
        return self.assertFalse(self.transport.connected)

    def test_clientConnectionFailed(self):
        self.transport.loseConnection()
        return self.assertFalse(self.transport.connected)

    @patch.object(client_amp.ClientProtocol, 'callRemote')
    def test_clientEndConnection(self, callRemote):
        self.transport.loseConnection()
        self.sp.end_connection()
        return self.assertTrue(callRemote.called)
