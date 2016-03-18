# coding=utf-8
import os
import sys
from mock import patch, MagicMock, Mock, PropertyMock


from PySide.QtTest import QTest
from PySide import QtGui, QtCore
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


class TestUserInterfaceParametersOperation(TestCase):

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
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(SatNetUI, 'UpdateFields')
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    @patch.object(SatNetUI, 'initConfiguration', return_value=True)
    def test_parametersAreLoadedWhenButtonIsClicked(self, createconnection,
                                                    initLogo, UpdateFields,
                                                    setParameters,
                                                    initConfiguration):
        """

        @param createconnection:
        @param initLogo:
        @param UpdateFields:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.argumentsdict)
        QTest.mouseClick(testUI.ButtonLoad, QtCore.Qt.LeftButton)
        return self.assertTrue(UpdateFields.called)

    # TODO Complete description
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(SatNetUI, 'SetConfiguration')
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    def test_configuration_opens_when_button_click(self, createconnection,
                                                   initLogo, SetConfiguration,
                                                   setArguments):
        """

        @param createconnection:
        @param initLogo:
        @param SetConfiguration:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.argumentsdict)
        QTest.mouseClick(testUI.ButtonConfiguration, QtCore.Qt.LeftButton)
        return self.assertTrue(SetConfiguration.called)

    # TODO Complete description
    @patch.object(Client, 'createconnection', return_value=True)
    @patch.object(SatNetUI, 'initLogo', return_value=True)
    @patch.object(SatNetUI, 'initButtons', return_value=True)
    @patch.object(SatNetUI, 'setParameters', return_value=True)
    @patch.object(misc, 'get_data_local_file')
    def _test_parameters_loaded_when_update_fields_Called(self,
                                                         createconnection,
                                                         initLogo, initButtons,
                                                         setParameters,
                                                         get_data_local_file,):
        """

        @param createconnection:
        @param initLogo:
        @param initButtons:
        @param setParameters:
        @param get_data_local_file:
        @return:
        """
        self.create_settings_file()
        testUI = SatNetUI(argumentsdict=self.argumentsdict)
        testUI.UpdateFields()
        return self.assertTrue(get_data_local_file.called)


# class TestUserInterfaceConnectionsOperation(TestCase):
#
#     # TODO Complete description
#     @patch('__main__.ConfigurationWindow')
#     def mockconfigurationwindow(ConfigurationWindow):
#         """
#
#         @return:
#         """
#         ConfigurationWindow.return_value = True
#         return ConfigurationWindow
#
#     #app = QtGui.QApplication(sys.argv)
#
#     # TODO Complete description
#     def createSettingsFile(self):
#         """
#
#         @return:
#         """
#         testFile = open(".settings", "w")
#         testFile.write("[User]\n"
#                        "username = test-sc-user\n"
#                        "password = sgongarpass\n"
#                        "slot_id = -1\n"
#                        "connection = none\n"
#                        "\n"
#                        "[Serial]\n"
#                        "serialport = /dev/ttyUSB0\n"
#                        "baudrate = 500000\n"
#                        "\n"
#                        "[udp]\n"
#                        "udpipreceive = 127.0.0.1\n"
#                        "udpportreceive = 1234\n"
#                        "udpipsend = 172.19.51.145\n"
#                        "udpportsend = 57009\n"
#                        "\n"
#                        "[tcp]\n"
#                        "tcpipreceive = 127.0.0.1\n"
#                        "tcpportreceive = 4321\n"
#                        "tcpipsend = 127.0.0.1\n"
#                        "tcpportsend = 1234\n"
#                        "\n"
#                        "[server]\n"
#                        "serverip = 172.19.51.133\n"
#                        "serverport = 25345\n"
#                        "\n"
#                        "[Connection]\n"
#                        "reconnection = no\n"
#                        "parameters = yes\n"
#                        "\n"
#                        "[Client]\n"
#                        "name = Universidade de Vigo\n"
#                        "attempts = 10")
#         testFile.close()
#
#     def setUp(self):
#         self.argumentsdict = {'username': 'test-sc-user',
#                               'udpipsend': '172.19.51.145',
#                               'baudrate': '500000',
#                               'name': 'Universidade de Vigo',
#                               'parameters': 'yes', 'tcpportsend': '1234',
#                               'tcpipsend': '127.0.0.1',
#                               'udpipreceive': '127.0.0.1', 'attempts': '10',
#                               'serverip': '172.19.51.133',
#                               'serialport': '/dev/ttyUSB0',
#                               'tcpportreceive': 4321, 'connection': 'none',
#                               'udpportreceive': 1234, 'serverport': 25345,
#                               'reconnection': 'no', 'udpportsend': '57009',
#                               'tcpipreceive': '127.0.0.1'}
#         self.createSettingsFile()
#
#     def tearDown(self):
#         os.remove('.settings')
#
#     # TODO Complete description
#     @patch.object(Client, 'createconnection', return_value=True)
#     @patch.object(SatNetUI, 'initLogo', return_value=True)
#     @patch.object(SatNetUI, 'NewConnection')
#     @patch.object(SatNetUI, 'setArguments', return_value=True)
#     def test_newConnectionWhenButtonClicked(self, createconnection,
#                                              initLogo, NewConnection,
#                                             setArguments):
#         """
#
#         @param createconnection:
#         @param initLogo:
#         @param NewConnection:
#         @return:
#         """
#         testUI = SatNetUI(argumentsdict=self.argumentsdict)
#         QTest.mouseClick(testUI.ButtonNew, QtCore.Qt.LeftButton)
#         return self.assertTrue(NewConnection.called)
#
#     # TODO Complete description
#     @patch.object(SatNetUI, 'initLogo', return_value=True)
#     @patch.object(Client, 'createconnection', return_value=True)
#     @patch.object(Client, 'setconnection')
#     @patch.object(SatNetUI, 'setArguments', return_value=True)
#     def test_loadReconnectionParametersOkNewConnection(self, initLogo,
#                                                        createconnection,
#                                                        setconnection,
#                                                        setArguments):
#         """
#
#         @param initLogo:
#         @param createconnection:
#         @param setconnection:
#         @return:
#         """
#         testUI = SatNetUI(argumentsdict=self.argumentsdict)
#         testUI.AutomaticReconnection.setChecked(True)
#         testUI.NewConnection(test=True)
#         return self.assertTrue(testUI.AutomaticReconnection.isChecked()), \
#                self.assertEquals(testUI.CONNECTION_INFO['reconnection'], 'yes')
#
#     # TODO Complete description
#     @patch.object(SatNetUI, 'initLogo', return_value=True)
#     @patch.object(Client, 'createconnection', return_value=True)
#     @patch.object(Client, 'setconnection')
#     @patch.object(SatNetUI, 'setArguments', return_value=True)
#     def test_loadReconnectionParametersNotNewConnection(self, initLogo,
#                                                         createconnection,
#                                                         setconnection,
#                                                         setArguments):
#         """
#
#         @param initLogo:
#         @param createconnection:
#         @param setconnection:
#         @return:
#         """
#         testUI = SatNetUI(argumentsdict=self.argumentsdict)
#         testUI.AutomaticReconnection.setChecked(False)
#         testUI.NewConnection(test=True)
#         return self.assertFalse(testUI.AutomaticReconnection.isChecked()), \
#                self.assertEquals(testUI.CONNECTION_INFO['reconnection'],
#                                  'no')
#
# class TestUserInterfaceDisconnectionsOperation(TestCase):
#
#     # TODO Complete description
#     @patch('__main__.ConfigurationWindow')
#     def mockconfigurationwindow(ConfigurationWindow):
#         """
#
#         @return:
#         """
#         ConfigurationWindow.return_value = True
#         return ConfigurationWindow
#
#
#     #app = QtGui.QApplication(sys.argv)
#
#     # TODO Complete description
#     def createSettingsFile(self):
#         """
#
#         @return:
#         """
#         testFile = open(".settings", "w")
#         testFile.write("[User]\n"
#                        "username = test-sc-user\n"
#                        "password = sgongarpass\n"
#                        "slot_id = -1\n"
#                        "connection = none\n"
#                        "\n"
#                        "[Serial]\n"
#                        "serialport = /dev/ttyUSB0\n"
#                        "baudrate = 500000\n"
#                        "\n"
#                        "[udp]\n"
#                        "udpipreceive = 127.0.0.1\n"
#                        "udpportreceive = 1234\n"
#                        "udpipsend = 172.19.51.145\n"
#                        "udpportsend = 57009\n"
#                        "\n"
#                        "[tcp]\n"
#                        "tcpipreceive = 127.0.0.1\n"
#                        "tcpportreceive = 4321\n"
#                        "tcpipsend = 127.0.0.1\n"
#                        "tcpportsend = 1234\n"
#                        "\n"
#                        "[server]\n"
#                        "serverip = 172.19.51.133\n"
#                        "serverport = 25345\n"
#                        "\n"
#                        "[Connection]\n"
#                        "reconnection = no\n"
#                        "parameters = yes\n"
#                        "\n"
#                        "[Client]\n"
#                        "name = Universidade de Vigo\n"
#                        "attempts = 10")
#         testFile.close()
#
#     def setUp(self):
#         self.argumentsdict = {'username': 'test-sc-user', 'udpipsend': '172.19.51.145', 'baudrate': '500000',
#                          'name': 'Universidade de Vigo', 'parameters': 'yes', 'tcpportsend': '1234',
#                          'tcpipsend': '127.0.0.1', 'udpipreceive': '127.0.0.1', 'attempts': '10',
#                          'serverip': '172.19.51.133', 'serialport': '/dev/ttyUSB0', 'tcpportreceive': 4321,
#                          'connection': 'none', 'udpportreceive': 1234, 'serverport': 25345,
#                          'reconnection': 'no', 'udpportsend': '57009', 'tcpipreceive': '127.0.0.1'}
#         self.createSettingsFile()
#
#     def tearDown(self):
#         os.remove('.settings')
#
#     # TODO Complete description
#     @patch.object(Client, 'createconnection', return_value=True)
#     @patch.object(SatNetUI, 'initLogo', return_value=True)
#     @patch.object(SatNetUI, 'CloseConnection')
#     @patch.object(SatNetUI, 'setArguments', return_value=True)
#     def test_closeConnectionWhenButtonClicked(self, createconnection,
#                                               initLogo, CloseConnection,
#                                               setArguments):
#         """
#
#         @param createconnection:
#         @param initLogo:
#         @param CloseConnection:
#         @return:
#         """
#         testUI = SatNetUI(argumentsdict=self.argumentsdict)
#         QTest.mouseClick(testUI.ButtonCancel, QtCore.Qt.LeftButton)
#         return self.assertTrue(CloseConnection.called)
#
#     # TODO Complete description
#     @patch.object(Client, 'createconnection', return_value=True)
#     @patch.object(SatNetUI, 'initLogo', return_value=True)
#     @patch.object(GroundStationInterface, 'clear_slots')
#     @patch.object(SatNetUI, 'setArguments', return_value=True)
#     def test_methodsAreCallWhenUserClosesConnection(self, createconnection,
#                                                     initLogo, clear_slots,
#                                                     setArguments):
#         """
#
#         @param createconnection:
#         @param initLogo:
#         @param clear_slots:
#         @return:
#         """
#         testUI = SatNetUI(argumentsdict=self.argumentsdict)
#         testUI.CloseConnection()
#         return self.assertTrue(clear_slots.called), self.assertTrue(testUI.ButtonNew.isEnabled()), \
#                self.assertFalse(testUI.ButtonCancel.isEnabled())
#
#
# class TestUserInterfaceCloseWindow(TestCase):
#     # TODO Complete description
#     @patch('__main__.ConfigurationWindow')
#     def mockconfigurationwindow(ConfigurationWindow):
#         """
#
#         @return:
#         """
#         ConfigurationWindow.return_value = True
#         return ConfigurationWindow
#
#
#     #app = QtGui.QApplication(sys.argv)
#
#     # TODO Complete description
#     def createSettingsFile(self):
#         """
#
#         @return:
#         """
#         testFile = open(".settings", "w")
#         testFile.write("[User]\n"
#                        "username = test-sc-user\n"
#                        "password = sgongarpass\n"
#                        "slot_id = -1\n"
#                        "connection = none\n"
#                        "\n"
#                        "[Serial]\n"
#                        "serialport = /dev/ttyUSB0\n"
#                        "baudrate = 500000\n"
#                        "\n"
#                        "[udp]\n"
#                        "udpipreceive = 127.0.0.1\n"
#                        "udpportreceive = 1234\n"
#                        "udpipsend = 172.19.51.145\n"
#                        "udpportsend = 57009\n"
#                        "\n"
#                        "[tcp]\n"
#                        "tcpipreceive = 127.0.0.1\n"
#                        "tcpportreceive = 4321\n"
#                        "tcpipsend = 127.0.0.1\n"
#                        "tcpportsend = 1234\n"
#                        "\n"
#                        "[server]\n"
#                        "serverip = 172.19.51.133\n"
#                        "serverport = 25345\n"
#                        "\n"
#                        "[Connection]\n"
#                        "reconnection = no\n"
#                        "parameters = yes\n"
#                        "\n"
#                        "[Client]\n"
#                        "name = Universidade de Vigo\n"
#                        "attempts = 10")
#         testFile.close()
#
#     def setUp(self):
#         self.argumentsdict = {'username': 'test-sc-user', 'udpipsend': '172.19.51.145', 'baudrate': '500000',
#                          'name': 'Universidade de Vigo', 'parameters': 'yes', 'tcpportsend': '1234',
#                          'tcpipsend': '127.0.0.1', 'udpipreceive': '127.0.0.1', 'attempts': '10',
#                          'serverip': '172.19.51.133', 'serialport': '/dev/ttyUSB0', 'tcpportreceive': 4321,
#                          'connection': 'none', 'udpportreceive': 1234, 'serverport': 25345,
#                          'reconnection': 'no', 'udpportsend': '57009', 'tcpipreceive': '127.0.0.1'}
#         self.createSettingsFile()
#
#     def tearDown(self):
#         os.remove('.settings')
#
#     # TODO Complete description
#     @patch.object(QtGui.QMessageBox, 'question',
#                   return_value=QtGui.QMessageBox.Yes)
#     @patch.object(SatNetUI, 'initLogo', return_value=True)
#     @patch.object(Client, 'createconnection', return_value=True)
#     @patch.object(GroundStationInterface, 'clear_slots')
#     @patch.object(Client, 'destroyconnection')
#     @patch.object(SatNetUI, 'setArguments', return_value=True)
#     def test_methodsAreCallWhenUserClosesWindow(self, question, initLogo,
#                                                 createconnection,
#                                                 clear_slots,
#                                                 destroyconnection,
#                                                 setArguments):
#         """ Methods are called when user closes the main window
#         Checks if the disconnection methods are call when user closes the main
#         window.
#         @param question: QMessageBox object mocked for test purpuses.
#         @param initLogo:
#         @param createconnection:
#         @param clear_slots:
#         @param destroyconnection:
#         @return:
#         """
#         testUI = SatNetUI(argumentsdict=self.argumentsdict)
#         eventmock = Mock
#         eventmock.ignore = MagicMock(return_value=True)
#         testUI.closeEvent(event=eventmock)
#         return self.assertTrue(clear_slots.called),\
#                self.assertTrue(destroyconnection.called),\
#                self.assertIsNot(eventmock.ignore, True)
#
#     # TODO Complete description
#     @patch.object(QtGui.QMessageBox, 'question',
#                   return_value=QtGui.QMessageBox.No)
#     @patch.object(SatNetUI, 'initLogo', return_value=True)
#     @patch.object(Client, 'createconnection', return_value=True)
#     @patch.object(SatNetUI, 'setArguments', return_value=True)
#     def test_userCancelsWindowClosing(self, question, initLogo,
#                                       createconnection,
#                                       setArguments):
#         """
#
#         @param question: QMessageBox object mocked for test purpuses.
#         @param initLogo: Method patched for
#         @param createconnection:
#         @return:
#         """
#         testUI = SatNetUI(argumentsdict=self.argumentsdict)
#         eventmock = Mock
#         eventmock.ignore = MagicMock(return_value=True)
#         testUI.closeEvent(event=eventmock)
#         return self.assertTrue(eventmock.ignore.called)