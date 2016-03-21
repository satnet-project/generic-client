# coding=utf-8
import os
import sys
from mock import patch, MagicMock, Mock, PropertyMock
from unittest import TestCase, main


from PySide.QtTest import QTest
from PySide import QtGui, QtCore

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


class TestUserInterfaceInterfacesOperation(TestCase):

    app = QtGui.QApplication(sys.argv)

    def create_settings_file(self):
        """ Create settings file.
        Create a settings file for tests purposes.

        @return: Nothing.
        """
        test_file = open(".settings", "w")
        test_file.write("[User]\n"
                        "institution = Universidade de Vigo\n"
                        "username = test-user-sc\n"
                        "password = pass\n"
                        "slot_id = -1\n"
                        "connection = udp\n"
                        "\n"
                        "[Serial]\n"
                        "serialport = /dev/ttyUSB0\n"
                        "baudrate = 500000\n"
                        "\n"
                        "[udp]\n"
                        "udpipreceive = 127.0.0.1\n"
                        "udpportreceive = 57109\n"
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
                        "serverip = 127.0.0.1\n"
                        "serverport = 25345\n"
                        "\n"
                        "[Connection]\n"
                        "reconnection = yes\n"
                        "parameters = no\n"
                        "attempts = 10\n")
        test_file.close()

    def setUp(self):
        self.arguments_dict = {'username': 'test-sc-user',
                              'udpipsend': '172.19.51.145',
                              'baudrate': '600000',
                              'institution': 'Universidade de Vigo',
                              'parameters': 'yes', 'tcpportsend': '1234',
                              'tcpipsend': '127.0.0.1',
                              'udpipreceive': '127.0.0.1', 'attempts': '10',
                              'serverip': '172.19.51.133',
                              'serialport': '/dev/ttyUSB0',
                              'tcpportreceive': 4321,
                              'connection': 'none', 'udpportreceive': 1234,
                              'serverport': 25345, 'reconnection': 'no',
                              'udpportsend': '57009',
                              'tcpipreceive': '127.0.0.1'}

        self.arguments_dict_empty = {'username': '', 'udpipsend': '',
                                     'baudrate': '', 'institution': '',
                                     'parameters': '', 'tcpportsend': '',
                                     'tcpipsend': '', 'udpipreceive': '',
                                     'attempts': '', 'serverip': '',
                                     'serialport': '', 'tcpportreceive': '',
                                     'connection': '', 'udpportreceive': '',
                                     'serverport': '', 'reconnection': '',
                                     'udpportsend': '', 'tcpipreceive': ''}

    def tearDown(self):
        os.remove('.settings')

    # TODO Complete description
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(Threads, 'runKISSThreadReceive', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_serial_interface_open_right_port_with_args(self, createconnection,
                                                        runKISSThreadReceive,
                                                        initLogo,
                                                        setArguments):
        """

        @param createconnection:
        @param runKISSThreadReceive:
        @param initLogo:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.arguments_dict)
        testUI.LabelConnection = Mock()
        testUI.LabelConnection.currentText = MagicMock(return_value='serial')
        testUI.openInterface()
        return self.assertTrue(runKISSThreadReceive.called), \
               self.assertEqual(int(testUI.CONNECTION_INFO['baudrate']), 600000)

    # TODO Complete description
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(Threads, 'runKISSThreadReceive', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_serial_interface_open_right_port_empty_args(self,
                                                         createconnection,
                                                         runKISSThreadReceive,
                                                         initLogo,
                                                         setArguments):
        """

        @param createconnection:
        @param runKISSThreadReceive:
        @param initLogo:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.arguments_dict_empty)
        testUI.LabelConnection = Mock()
        testUI.LabelConnection.currentText = MagicMock(return_value='serial')
        testUI.openInterface()
        return self.assertTrue(runKISSThreadReceive.called), \
               self.assertEqual(int(testUI.CONNECTION_INFO['baudrate']), 500000)


    # TODO Complete description
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(Threads, 'stopKISSThread', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_serial_interface_close(self, createconnection, stopKISSThread,
                                    initLogo, setArguments):
        """

        @param createconnection:
        @param stopKISSThread:
        @param initLogo:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.arguments_dict)
        testUI.connection = 'serial'
        testUI.stopInterface()
        return self.assertTrue(stopKISSThread.called)

    # TODO Complete description
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(Threads, 'runUDPThreadReceive')
    @patch.object(Threads, 'runUDPThreadSend')
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_udp_interface_open_with_args(self, createconnection, initLogo,
                                          runUDPThreadReceive,
                                          runUDPThreadSend,
                                          setArguments):
        """

        @param createconnection:
        @param initLogo:
        @param runUDPThreadReceive:
        @param runUDPThreadSend:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.arguments_dict)
        testUI.LabelConnection = Mock()
        testUI.LabelConnection.currentText = MagicMock(return_value='udp')
        testUI.openInterface()
        # LabelConnection is a Mock object so its state can be checked
        return self.assertTrue(runUDPThreadReceive.called),\
               self.assertTrue(runUDPThreadSend.called), \
               self.assertIs(testUI.connection, 'udp'),\
               self.assertTrue(testUI.stopInterfaceButton.isEnabled())

    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(Threads, 'runUDPThreadReceive')
    @patch.object(Threads, 'runUDPThreadSend')
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_udp_interface_open_empty_args(self, createconnection, initLogo,
                                          runUDPThreadReceive,
                                          runUDPThreadSend,
                                          setArguments):
        """

        @param createconnection:
        @param initLogo:
        @param runUDPThreadReceive:
        @param runUDPThreadSend:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.arguments_dict_empty)
        testUI.LabelConnection = Mock()
        testUI.LabelConnection.currentText = MagicMock(return_value='udp')
        testUI.openInterface()
        # LabelConnection is a Mock object so its state can be checked
        return self.assertTrue(runUDPThreadReceive.called),\
               self.assertTrue(runUDPThreadSend.called), \
               self.assertIs(testUI.connection, 'udp'),\
               self.assertTrue(testUI.stopInterfaceButton.isEnabled())

    # TODO Complete description
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(Threads, 'stopUDPThreadReceive')
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_udp_interface_close(self, createconnection, initLogo,
                                 stopUDPThreadReceive, setArguments):
        """

        @param createconnection:
        @param initLogo:
        @param stopUDPThreadReceive:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.arguments_dict)
        testUI.connection = 'udp'
        testUI.stopInterface()
        return self.assertTrue(stopUDPThreadReceive.called),\
               self.assertIs(testUI.connection, 'udp'), \
               self.assertFalse(testUI.stopInterfaceButton.isEnabled())

if __name__ == "__main__":
    main()