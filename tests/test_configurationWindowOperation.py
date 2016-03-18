# coding=utf-8
import os
import sys
import ConfigParser
from unittest import TestCase


from mock import patch
from PySide.QtTest import QTest
from PySide import QtGui, QtCore
# from twisted.trial.unittest import TestCase

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))
from configurationWindow import ConfigurationWindow
from errors import SettingsCorrupted


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

    # TODO Complete description
    def create_wrong_settings_file(self):
        """

        @return:
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
                        "udpportreceive = 57008\n"
                        "udpipsend = 127.0.0.2\n"
                        "udpportsend = 57009\n"
                        "\n"
                        "[tcp]\n"
                        "tcpipreceive = 127.0.0.3\n"
                        "tcpportreceive = 57010\n"
                        "tcpipsend = 127.0.0.4\n"
                        "tcpportsend = 57011\n"
                        "\n"
                        "[server]\n"
                        "serverip = 127.0.0.5\n"
                        "serverport = 57012\n"
                        "\n"
                        "[Connection]\n"
                        "parameters = no\n"
                        "attempts = 10\n")
        test_file.close()
    # TODO Complete description
    def create_settings_file(self):
        """

        @return:
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
                        "udpportreceive = 57008\n"
                        "udpipsend = 127.0.0.2\n"
                        "udpportsend = 57009\n"
                        "\n"
                        "[tcp]\n"
                        "tcpipreceive = 127.0.0.3\n"
                        "tcpportreceive = 57010\n"
                        "tcpipsend = 127.0.0.4\n"
                        "tcpportsend = 57011\n"
                        "\n"
                        "[server]\n"
                        "serverip = 127.0.0.5\n"
                        "serverport = 57012\n"
                        "\n"
                        "[Connection]\n"
                        "reconnection = yes\n"
                        "parameters = no\n"
                        "attempts = 10\n")
        test_file.close()

    def setUp(self):
        pass

    def tearDown(self):
        """ Tear down method.
        Between each test the settings configuration file must be remove.
        @return: Nothing.
        """
        os.remove('.settings')

    # TODO How-to assert a text?
    def test_open_window_with_wrong_settings_file(self):
        """

        @return: assertIs statement.
        """
        self.create_wrong_settings_file()
        return self.assertRaises(SettingsCorrupted, ConfigurationWindow)

    def test_read_configuration_file(self):
        """ Reads configuration file.
        Creates a new ConfigurationWindow object which loads the settings
        from the mocked .settings file created.

        @return: Few assertEqual methods who checks if the registers
        saved are correct.
        """
        self.create_settings_file()
        test_save = ConfigurationWindow()

        self.assertEqual(str(test_save.FieldLabelServer.text()),
                         '127.0.0.5')
        self.assertEqual(str(test_save.FieldLabelPort.text()),
                         '57012')
        self.assertEqual(str(test_save.FieldLabelUDPIpSend.text()),
                         '127.0.0.2')
        self.assertEqual(str(test_save.FieldLabelUDPPortSend.text()),
                         '57009')
        self.assertEqual(str(test_save.FieldLabelUDPIPReceive.text()),
                         '127.0.0.1')
        self.assertEqual(str(test_save.FieldLabelUDPPortRececeive.text()),
                         '57008')
        self.assertEqual(str(test_save.FieldLabelTCPIPSend.text()),
                         '127.0.0.4')
        self.assertEqual(str(test_save.FieldLabelTCPPortSend.text()),
                         '57011')
        self.assertEqual(str(test_save.FieldLabelTCPIPReceive.text()),
                         '127.0.0.3')
        self.assertEqual(str(test_save.FieldLabelTCPPortRececeive.text()),
                         '57010')

    def test_save_configuration_when_button_clicked(self):
        """ Save configuration when the button is clicked
        Sets the content of the text insertion fields and runs the function
        responsible for storing the fields.

        Checks if the saved records on the file are equals to the records
        desired.
        @return: a bunch of assertEqual statements.
        """
        self.create_settings_file()
        test_save = ConfigurationWindow()
        test_save.FieldLabelServer.setText('133.51.19.172')
        test_save.FieldLabelPort.setText('54352')
        test_save.FieldLabelUDPIpSend.setText('145.51.19.172')
        test_save.FieldLabelUDPPortSend.setText('90075')
        test_save.FieldLabelUDPIPReceive.setText('1.0.0.127')
        test_save.FieldLabelUDPPortRececeive.setText('4321')
        test_save.FieldLabelTCPIPSend.setText('1.0.0.127')
        test_save.FieldLabelTCPPortSend.setText('4321')
        test_save.FieldLabelTCPIPReceive.setText('1.0.0.127')
        test_save.FieldLabelTCPPortRececeive.setText('1234')

        test_save.save()
        config = ConfigParser.SafeConfigParser()
        config.read(".settings")
        field_label_server = config.get('server', 'serverip')
        field_label_port = config.get('server', 'serverport')
        field_label_UDP_IP_send = config.get('udp', 'udpipsend')
        field_label_UDP_port_send = config.get('udp', 'udpportsend')
        field_label_UDP_IP_receive = config.get('udp', 'udpipreceive')
        field_label_UDP_port_receive = config.get('udp', 'udpportreceive')
        field_label_TCP_IP_send = config.get('tcp', 'tcpipsend')
        field_label_TCP_port_send = config.get('tcp', 'tcpportsend')
        field_label_TCP_IP_receive = config.get('tcp', 'tcpipreceive')
        field_label_TCP_port_receive = config.get('tcp', 'tcpportreceive')

        self.assertEqual('133.51.19.172', str(field_label_server))
        self.assertEqual('54352', str(field_label_port))
        self.assertEqual('145.51.19.172', str(field_label_UDP_IP_send))
        self.assertEqual('90075', str(field_label_UDP_port_send))
        self.assertEqual('1.0.0.127', str(field_label_UDP_IP_receive))
        self.assertEqual('4321', str(field_label_UDP_port_receive))
        self.assertEqual('1.0.0.127', str(field_label_TCP_IP_send))
        self.assertEqual('4321', str(field_label_TCP_port_send))
        self.assertEqual('1.0.0.127', str(field_label_TCP_IP_receive))
        self.assertEqual('1234', str(field_label_TCP_port_receive))

    @patch.object(ConfigurationWindow, 'closeWindow')
    def test_buttons_operation_close_window(self, closeWindow):
        """ Window will close by pressing the button.
        Creates a new configuration window, then, the close button will be
        press.

        @param closeWindow: Method closedWindow patched from
        ConfigurationWindow class.
        @return: A assertEqual statement which checks if closeWindow is called.
        """
        self.create_settings_file()
        testOperation = ConfigurationWindow()
        closebutton = testOperation.buttonBox.button(
            QtGui.QDialogButtonBox.Close)
        QTest.mouseClick(closebutton, QtCore.Qt.LeftButton)
        return self.assertEqual(int(closeWindow.call_count), 1)

    # TODO Complete description
    @patch.object(ConfigurationWindow, 'save')
    def test_buttons_operation_save_registers(self, save):
        """ Save method will be call by pressing the button.


        @param save: method save patched from ConfigurationWindow class.
        @return: a assertEqual statement which checks if save is called.
        """
        self.create_settings_file()
        testOperation = ConfigurationWindow()
        savebutton = testOperation.buttonBox.button(
            QtGui.QDialogButtonBox.Save)
        QTest.mouseClick(savebutton, QtCore.Qt.LeftButton)
        return self.assertEqual(int(save.call_count), 1)

    # TODO Complete description
    @patch.object(ConfigurationWindow, 'close')
    def test_closeFunctionCalledWhenQuitWindow(self, close):
        """

        @param close: Method close patched from ConfigurationWindow class.
        @return: A assertEqual statement which checks if close method is
        called.
        """
        self.create_settings_file()
        testWindowConfiguration = ConfigurationWindow()
        testWindowConfiguration.closeWindow()
        return self.assertEqual(int(close.call_count), 1)
