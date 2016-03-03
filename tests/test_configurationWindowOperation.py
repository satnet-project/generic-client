# coding=utf-8
import os
import sys
import ConfigParser

# Dependencies for the tests
from mock import patch, MagicMock, Mock, PropertyMock

from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore

from serial import serialutil

from twisted.trial.unittest import TestCase

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))
from client_ui import SatNetUI
from client_amp import Client
from threads import Threads
import misc
from gs_interface import GroundStationInterface, KISSThread
from configurationWindow import ConfigurationWindow


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


class TestUserConfigurationInterfaceOperation(TestCase):

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
        self.createSettingsFile()

    def tearDown(self):
        os.remove('.settings')


    def _test_readConfiguration(self):
        """

        @return: assertIsNone statement
        """
        testSave = ConfigurationWindow()

        self.assertEqual(str(testSave.FieldLabelServer.text()), '172.19.51.133')
        self.assertEqual(str(testSave.FieldLabelPort.text()), '25345')
        self.assertEqual(str(testSave.FieldLabelUDPIpSend.text()), '172.19.51.145')
        self.assertEqual(str(testSave.FieldLabelUDPPortSend.text()), '57009')
        self.assertEqual(str(testSave.FieldLabelUDPIPReceive.text()), '127.0.0.1')
        self.assertEqual(str(testSave.FieldLabelUDPPortRececeive.text()), '1234')
        self.assertEqual(str(testSave.FieldLabelTCPIPSend.text()), '127.0.0.1')
        self.assertEqual(str(testSave.FieldLabelTCPPortSend.text()), '1234')
        self.assertEqual(str(testSave.FieldLabelTCPIPReceive.text()), '127.0.0.1')
        self.assertEqual(str(testSave.FieldLabelTCPPortRececeive.text()), '4321')

    def _test_saveConfigurationWhenButtonClicked(self):
        testSave = ConfigurationWindow()
        testSave.FieldLabelServer.setText('133.51.19.172')
        testSave.FieldLabelPort.setText('54352')
        testSave.FieldLabelUDPIpSend.setText('145.51.19.172')
        testSave.FieldLabelUDPPortSend.setText('90075')
        testSave.FieldLabelUDPIPReceive.setText('1.0.0.127')
        testSave.FieldLabelUDPPortRececeive.setText('4321')
        testSave.FieldLabelTCPIPSend.setText('1.0.0.127')
        testSave.FieldLabelTCPPortSend.setText('4321')
        testSave.FieldLabelTCPIPReceive.setText('1.0.0.127')
        testSave.FieldLabelTCPPortRececeive.setText('1234')

        testSave.save()
        config = ConfigParser.SafeConfigParser()
        config.read(".settings")
        FieldLabelServer = config.get('server', 'serverip')
        FieldLabelPort = config.get('server', 'serverport')
        FieldLabelUDPIPSend = config.get('udp', 'udpipsend')
        FieldLabelUDPPortSend = config.get('udp', 'udpportsend')
        FieldLabelUDPIPReceive = config.get('udp', 'udpipreceive')
        FieldLabelUDPPortReceive = config.get('udp', 'udpportreceive')
        FieldLabelTCPIPSend = config.get('tcp', 'tcpipsend')
        FieldLabelTCPPortSend = config.get('tcp', 'tcpportsend')
        FieldLabelTCPIPReceive = config.get('tcp', 'tcpipreceive')
        FieldLabelTCPPortReceive = config.get('tcp', 'tcpportreceive')

        self.assertEqual('133.51.19.172', str(FieldLabelServer))
        self.assertEqual('54352', str(FieldLabelPort))
        self.assertEqual('145.51.19.172', str(FieldLabelUDPIPSend))
        self.assertEqual('90075', str(FieldLabelUDPPortSend))
        self.assertEqual('1.0.0.127', str(FieldLabelUDPIPReceive))
        self.assertEqual('4321', str(FieldLabelUDPPortReceive))
        self.assertEqual('1.0.0.127', str(FieldLabelTCPIPSend))
        self.assertEqual('4321', str(FieldLabelTCPPortSend))
        self.assertEqual('1.0.0.127', str(FieldLabelTCPIPReceive))
        self.assertEqual('1234', str(FieldLabelTCPPortReceive))

    @patch.object(ConfigurationWindow, 'closeWindow')
    def test_buttonsOperationCloseWindow(self, closeWindow):
        testOperation = ConfigurationWindow()
        closebutton = testOperation.buttonBox.button(QtGui.QDialogButtonBox.Close)
        QTest.mouseClick(closebutton, QtCore.Qt.LeftButton)
        return self.assertEqual(int(closeWindow.call_count), 1)

    @patch.object(ConfigurationWindow, 'save')
    def test_buttonsOperationSaveCall(self, save):
        testOperation = ConfigurationWindow()
        savebutton = testOperation.buttonBox.button(QtGui.QDialogButtonBox.Save)
        QTest.mouseClick(savebutton, QtCore.Qt.LeftButton)
        return self.assertEqual(int(save.call_count), 1)

    @patch.object(ConfigurationWindow, 'close')
    def _test_closeFunctionCalledWhenQuitWindow(self, close):
        """

        @param close: patch method
        @return: assertEqual statement
        """
        testWindowConfiguration = ConfigurationWindow()
        testWindowConfiguration.closeWindow()
        return self.assertEqual(int(close.call_count), 1)
