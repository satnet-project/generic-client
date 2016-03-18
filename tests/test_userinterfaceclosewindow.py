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


class TestUserInterfaceCloseWindow(TestCase):
    # TODO Complete description
    @patch('__main__.ConfigurationWindow')
    def mockconfigurationwindow(ConfigurationWindow):
        """

        @return:
        """
        ConfigurationWindow.return_value = True
        return ConfigurationWindow


    app = QtGui.QApplication(sys.argv)

    # TODO Complete description
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
        self.argumentsdict = {'username': 'test-sc-user',
                              'udpipsend': '172.19.51.145',
                              'baudrate': '500000',
                              'institution': 'Universidade de Vigo',
                              'parameters': 'yes', 'tcpportsend': '1234',
                              'tcpipsend': '127.0.0.1',
                              'udpipreceive': '127.0.0.1', 'attempts': '10',
                              'serverip': '172.19.51.133',
                              'serialport': '/dev/ttyUSB0',
                              'tcpportreceive': 4321, 'connection': 'none',
                              'udpportreceive': 1234, 'serverport': 25345,
                              'reconnection': 'no', 'udpportsend': '57009',
                              'tcpipreceive': '127.0.0.1'}

    def tearDown(self):
        os.remove('.settings')

    # TODO Complete description
    @patch.object(QtGui.QMessageBox, 'question',
                  return_value=QtGui.QMessageBox.Yes)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(GroundStationInterface, 'clear_slots')
    @patch.object(Client, 'destroyconnection')
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_methodsAreCallWhenUserClosesWindow(self, question, initLogo,
                                                createconnection,
                                                clear_slots,
                                                destroyconnection,
                                                setArguments):
        """ Methods are called when user closes the main window
        Checks if the disconnection methods are call when user closes the main
        window.
        @param question: QMessageBox object mocked for test purpuses.
        @param initLogo:
        @param createconnection:
        @param clear_slots:
        @param destroyconnection:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.argumentsdict)
        eventmock = Mock
        eventmock.ignore = MagicMock(return_value=True)
        testUI.closeEvent(event=eventmock)
        return self.assertTrue(clear_slots.called),\
               self.assertTrue(destroyconnection.called),\
               self.assertIsNot(eventmock.ignore, True)

    # TODO Complete description
    @patch.object(QtGui.QMessageBox, 'question',
                  return_value=QtGui.QMessageBox.No)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_userCancelsWindowClosing(self, question, initLogo,
                                      createconnection,
                                      setArguments):
        """

        @param question: QMessageBox object mocked for test purpuses.
        @param initLogo: Method patched for
        @param createconnection:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.argumentsdict)
        eventmock = Mock
        eventmock.ignore = MagicMock(return_value=True)
        testUI.closeEvent(event=eventmock)
        return self.assertTrue(eventmock.ignore.called)

if __name__ == "__main__":
    main()