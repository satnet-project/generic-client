# coding=utf-8
import os
import sys
import pty

# Dependencies for the tests
from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport
from twisted.internet.protocol import Factory

from twisted.protocols.amp import AMP, BoxDispatcher

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))

from ampCommands import NotifyMsg
from client_ui import *
from gs_interface import GroundStationInterface
from threads import Threads

from serial.serialutil import SerialException

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


class TestClientProtocolReceiveFrame(TestCase):
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

        self.sp = ClientProtocol(CONNECTION_INFO, gsi, threads)
        self.sp.factory = MockFactory()
        self.transport = StringTransport()
        self.sp.makeConnection(self.transport)

        self.transport.protocol = self.sp

        self.correctFrame = ("00:82:a0:00:00:53:45:52:50:2d:42:30:91:1d:1b:03:" +
                             "8d:0b:5c:03:02:28:01:9c:01:ab:02:4c:02:98:01:da:" +
                             "02:40:00:00:00:10:0a:46:58:10:00:c4:9d:cb:a2:21:39")

        self.wrongFrame = 9

    def tearDown(self):
        pass

    def test_clientReceiveRightString(self):
        self.sp.callRemote(NotifyMsg, sMsg=self.correctFrame)

    def test_clientReceiveWrongString(self):
        return self.assertRaises(TypeError, self.sp.callRemote,
                                 NotifyMsg, sMsg=self.wrongFrame)


class TestNotifyMsgSendMessageBack(TestCase):
    def setUp(self):
        self.CONNECTION_INFO = {'username': 'satnet_admin', 'password': 'pass', 'udpipsend': '172.19.51.145',
                                'baudrate': '500000', 'name': 'Universidade de Vigo', 'parameters': 'yes',
                                'tcpportsend': '1234', 'tcpipsend': '127.0.0.1', 'udpipreceive': '127.0.0.1',
                                'attempts': '10', 'serverip': '172.19.51.143', 'serialport': 'self.s_name',
                                'tcpportreceive': 4321, 'connection': 'udp', 'udpportreceive': 57008,
                                'serverport': 25345, 'reconnection': 'no', 'udpportsend': '57009',
                                'tcpipreceive': '127.0.0.1'}

        self.correctFrame = ("00:82:a0:00:00:53:45:52:50:2d:42:30:91:1d:1b:03:" +
                             "8d:0b:5c:03:02:28:01:9c:01:ab:02:4c:02:98:01:da:" +
                             "02:40:00:00:00:10:0a:46:58:10:00:c4:9d:cb:a2:21:39")

        self.correctFrame = bytearray(self.correctFrame)

    def _test_serialConnectionSelectedWithPortAvailable(self):
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)

        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'serial'

        # Lastest version of PySerial can't handle pseudo serial ports
        # https://github.com/pyserial/pyserial/issues/76

        master, slave = pty.openpty()
        s_name = os.ttyname(slave)

        self.CONNECTION_INFO['serialport'] = s_name
        serialconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correctFrame)

        return self.assertTrue(serialconnectionresponse['bResult'])

    def test_serialConnectionSelectedWithoutPortAvailable(self):
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)

        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'serial'

        return self.assertRaises(SerialException, self.sp.vNotifyMsg, self.correctFrame)

    def test_udpConnectionReachable(self):
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)

        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'udp'

        udpconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correctFrame)

        return self.assertTrue(udpconnectionresponse['bResult'])

    def _test_udpConnectionUnreachable(self):
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)

        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'udp'

        # To-implemented.

    def test_tcpConnectionReachable(self):
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)

        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'tcp'

        tcpconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correctFrame)

        return self.assertTrue(tcpconnectionresponse['bResult'])

    def test_noConnectionSelected(self):
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)

        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'none'

        noneconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correctFrame)

        return self.assertTrue(noneconnectionresponse['bResult'])
