# coding=utf-8
import os
import sys

# Dependencies for the tests
from mock import patch, Mock, MagicMock

from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore

from twisted.trial.unittest import TestCase

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))

from errors import WrongFormatNotification, FrameNotProcessed, ConnectionNotEnded
from client_ui import SatNetUI
from client_amp import Client

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


class TestUserInterfaceOperation(TestCase):

    def mockcreateconnection(self):
        return True

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
        self.argumentsdict = {'username': 'test-sc-user', 'udpipsend': '172.19.51.145', 'baudrate': '500000',
                         'name': 'Universidade de Vigo', 'parameters': 'yes', 'tcpportsend': '1234',
                         'tcpipsend': '127.0.0.1', 'udpipreceive': '127.0.0.1', 'attempts': '10',
                         'serverip': '172.19.51.133', 'serialport': '/dev/ttyUSB0', 'tcpportreceive': 4321,
                         'connection': 'none', 'udpportreceive': 1234, 'serverport': 25345,
                         'reconnection': 'no', 'udpportsend': '57009', 'tcpipreceive': '127.0.0.1'}
        self.createSettingsFile()

    def tearDown(self):
        os.remove('.settings')

    @patch.object(Client, 'createconnection', mockcreateconnection)
    @patch.object(SatNetUI, 'NewConnection')
    def test_newConnectionWhenButtonClicked(self, NewConnection):
        testUI = SatNetUI(argumentsdict=self.argumentsdict)
        QTest.mouseClick(testUI.ButtonNew, QtCore.Qt.LeftButton)
        return self.assertTrue(NewConnection.called)

    """
    This button is disabled at first instance.
    """
    @patch.object(Client, 'createconnection', mockcreateconnection)
    @patch.object(SatNetUI, 'CloseConnection')
    def test_closeConnectionWhenButtonClicked(self, CloseConnection):
        testUI = SatNetUI(argumentsdict=self.argumentsdict)
        QTest.mouseClick(testUI.ButtonCancel, QtCore.Qt.LeftButton)
        return self.assertFalse(CloseConnection.called)

    @patch.object(Client, 'createconnection', mockcreateconnection)
    @patch.object(SatNetUI, 'UpdateFields')
    def test_runKISSThreadCorrectly(self, UpdateFIelds):
        self.testUI = SatNetUI(argumentsdict=self.argumentsdict)
        QTest.mouseClick(self.testUI.ButtonLoad, QtCore.Qt.LeftButton)
        return self.assertTrue(UpdateFIelds.called)

    @patch.object(Client, 'createconnection', mockcreateconnection)
    @patch.object(SatNetUI, 'SetConfiguration')
    def test_configurationOpenedWhenButtonClicked(self, SetConfiguration):
        testUI = SatNetUI(argumentsdict=self.argumentsdict)
        QTest.mouseClick(testUI.ButtonConfiguration, QtCore.Qt.LeftButton)
        return self.assertTrue(SetConfiguration.called)

    def _test_parametersLoadedWhenUpdateFieldsIsCalled(self):
        pass


    # @patch.object(GroundStationInterface, '_updateLocalFile')
    # def test_groundstationInterfaceConnectedReceiveCorrectFrameBadProcessed(self, _updateLocalFile):
    #     AMP._processframe = MagicMock()
    #     AMP._processframe.side_effect = self.mock_badprocessframe(self.correctFrame)
    #     self.gsi.AMP = AMP
    #     return self.assertRaises(FrameNotProcessed, self.gsi._manageFrame, self.correctFrame)
    #
    # @patch.object(GroundStationInterface, '_updateLocalFile')
    # def test_groundstationInterfaceConnectedReceiveCorrectFrame(self, _updateLocalFile):
    #     AMP._processframe = MagicMock()
    #     AMP._processframe.side_effect = self.mock_goodprocessframe(self.correctFrame)
    #     self.gsi.AMP = AMP
    #     self.gsi._manageFrame(self.correctFrame)
    #     return self.assertTrue(_updateLocalFile.called), self.assertTrue(AMP._processframe.called)
    #
    # @patch.object(GroundStationInterface, '_updateLocalFile')
    # def test_groundstationInterfaceDisconnectedReceiveCorrectFrame(self, _updateLocalFile):
    #     self.gsi.AMP = None
    #     self.gsi._manageFrame(self.correctFrame)
    #     return self.assertTrue(_updateLocalFile.called)
    #
    # def test_groundstationInterfaceConnectedReceiveBadFrame(self):
    #     self.gsi.AMP = AMP
    #     return self.assertRaises(WrongFormatNotification, self.gsi._manageFrame, self.wrongFrame)
    #
    # def test_groundstationInterfaceDisconnectedReceiveBadFrame(self):
    #     self.gsi.AMP = None
    #     return self.assertRaises(WrongFormatNotification, self.gsi._manageFrame, self.wrongFrame)
    #
    # def test_groundstationInterfaceUpdateLocalFileCorrectFrame(self):
    #     return self.assertTrue(self.gsi._updateLocalFile(self.correctFrame))
    #
    # def test_groundstationInterfaceCallsEndRemoteRightAnswer(self):
    #     AMP.end_connection = MagicMock()
    #     AMP.end_connection.side_effect = self.mock_goodendconnection()
    #     self.gsi.AMP = AMP
    #     return self.assertIsNone(self.gsi.clear_slots())
    #
    # def test_groundstationInterfaceCallsEndRemoteWrongAnswer(self):
    #     AMP.end_connection = MagicMock()
    #     AMP.end_connection.side_effect = self.mock_badendconnection()
    #     self.gsi.AMP = AMP
    #     return self.assertRaises(ConnectionNotEnded, self.gsi.clear_slots)
    #
    # def test_groundstationInterfaceEnableAMP(self):
    #     self.gsi.connectProtocol(AMP)
    #     return self.assertIsInstance(self.gsi.AMP, object)
    #
    # def test_groundstationInterfaceDisabledAMP(self):
    #     self.gsi.disconnectProtocol()
    #     return self.assertIsNone(self.gsi.AMP)
