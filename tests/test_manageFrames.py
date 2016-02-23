# coding=utf-8
import os
import sys
import pty

# Dependencies for the tests
from mock import patch, Mock, MagicMock

from twisted.trial.unittest import TestCase
from twisted.protocols.amp import AMP

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))

from gs_interface import GroundStationInterface
from errors import WrongFormatNotification, FrameNotProcessed, ConnectionNotEnded


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


class TestGroundStationInterfaceFramesManagement(TestCase):

    def mock_goodprocessframe(self, frame):
        return frame

    def mock_badprocessframe(self, frame):
        return Exception

    def mock_goodendconnection(self):
        return None

    def mock_badendconnection(self):
        return Exception

    def setUp(self):
        CONNECTION_INFO = {'username': 'satnet_admin', 'password': 'pass', 'udpipsend': '172.19.51.145',
                           'baudrate': '500000', 'name': 'Universidade de Vigo', 'parameters': 'yes',
                           'tcpportsend': '1234', 'tcpipsend': '127.0.0.1', 'udpipreceive': '127.0.0.1',
                           'attempts': '10', 'serverip': '172.19.51.143', 'serialport': '/dev/ttyUSB0',
                           'tcpportreceive': 4321, 'connection': 'udp', 'udpportreceive': 57008,
                           'serverport': 25345, 'reconnection': 'no', 'udpportsend': '57009',
                           'tcpipreceive': '127.0.0.1'}

        GS = 'VigoTest'

        self.gsi = GroundStationInterface(CONNECTION_INFO, GS, AMP)

        self.correctFrame = ("00:82:a0:00:00:53:45:52:50:2d:42:30:91:1d:1b:03:" +
                             "8d:0b:5c:03:02:28:01:9c:01:ab:02:4c:02:98:01:da:" +
                             "02:40:00:00:00:10:0a:46:58:10:00:c4:9d:cb:a2:21:39")

        self.correctFrame = bytearray(self.correctFrame)
        self.wrongFrame = 9

    def tearDown(self):
        pass

    @patch.object(GroundStationInterface, '_updateLocalFile')
    def test_groundstationInterfaceConnectedReceiveCorrectFrameBadProcessed(self, _updateLocalFile):
        AMP._processframe = MagicMock()
        AMP._processframe.side_effect = self.mock_badprocessframe(self.correctFrame)
        self.gsi.AMP = AMP
        return self.assertRaises(FrameNotProcessed, self.gsi._manageFrame, self.correctFrame)

    @patch.object(GroundStationInterface, '_updateLocalFile')
    def test_groundstationInterfaceConnectedReceiveCorrectFrame(self, _updateLocalFile):
        AMP._processframe = MagicMock()
        AMP._processframe.side_effect = self.mock_goodprocessframe(self.correctFrame)
        self.gsi.AMP = AMP
        self.gsi._manageFrame(self.correctFrame)
        return self.assertTrue(_updateLocalFile.called), self.assertTrue(AMP._processframe.called)

    @patch.object(GroundStationInterface, '_updateLocalFile')
    def test_groundstationInterfaceDisconnectedReceiveCorrectFrame(self, _updateLocalFile):
        self.gsi.AMP = None
        self.gsi._manageFrame(self.correctFrame)
        return self.assertTrue(_updateLocalFile.called)

    def test_groundstationInterfaceConnectedReceiveBadFrame(self):
        self.gsi.AMP = AMP
        return self.assertRaises(WrongFormatNotification, self.gsi._manageFrame, self.wrongFrame)

    def test_groundstationInterfaceDisconnectedReceiveBadFrame(self):
        self.gsi.AMP = None
        return self.assertRaises(WrongFormatNotification, self.gsi._manageFrame, self.wrongFrame)

    def test_groundstationInterfaceUpdateLocalFileCorrectFrame(self):
        return self.assertTrue(self.gsi._updateLocalFile(self.correctFrame))

    def test_groundstationInterfaceCallsEndRemoteRightAnswer(self):
        AMP.end_connection = MagicMock()
        AMP.end_connection.side_effect = self.mock_goodendconnection()
        self.gsi.AMP = AMP
        return self.assertIsNone(self.gsi.clear_slots())

    def test_groundstationInterfaceCallsEndRemoteWrongAnswer(self):
        AMP.end_connection = MagicMock()
        AMP.end_connection.side_effect = self.mock_badendconnection()
        self.gsi.AMP = AMP
        return self.assertRaises(ConnectionNotEnded, self.gsi.clear_slots)

    def test_groundstationInterfaceEnableAMP(self):
        self.gsi.connectProtocol(AMP)
        return self.assertIsInstance(self.gsi.AMP, object)

    def test_groundstationInterfaceDisabledAMP(self):
        self.gsi.disconnectProtocol()
        return self.assertIsNone(self.gsi.AMP)
