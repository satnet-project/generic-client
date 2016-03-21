# coding=utf-8
import os
import sys
from mock import patch, MagicMock, Mock
from unittest import TestCase, main


from PySide import QtGui

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))
from threads import Threads
from misc import get_data_local_file
from gs_interface import GroundStationInterface, OperativeUDPThreadReceive
from gs_interface import OperativeUDPThreadSend


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


settings_test_file = '.settings'

class TestUserInterfaceInterfacesThreads(TestCase):
    """
    This class checks the calls to the threads definition methods.
    The start/stop methods are located at Threads class.
    The definitions can be found at gs_interface module.
    """

    app = QtGui.QApplication(sys.argv)

    def create_settings_file(self):
        """ Create settings file.
        Create a settings file for tests purposes.

        @return: Nothing.
        """
        test_file = open(settings_test_file, "w")
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
        pass

    def tearDown(self):
        os.remove(settings_test_file)

    # TODO Complete description
    def _test_udp_class_thread_receive_created(self):
        """

        :return:
        """
        OperativeUDPThreadReceive = MagicMock(return_value=True)

        AMP = MagicMock(return_value=True)
        self.create_settings_file()
        connect_info = get_data_local_file(settings_test_file)
        gsi = GroundStationInterface(connect_info, 'Vigo', AMP)

        test_threads = Threads(settings_test_file, gsi)

        return self.assertEqual(test_threads.runUDPThreadReceive(), None)

    # TODO Complete description
    def test_udp_class_thread_send_created(self):
        """

        :return:
        """
        AMP = MagicMock(return_value=True)
        self.create_settings_file()
        connect_info = get_data_local_file(settings_test_file)
        gsi = GroundStationInterface(connect_info, 'Vigo', AMP)
        test_threads = Threads(settings_test_file, gsi)

        test_threads.runUDPThreadSend()

        return self.assertIsInstance(test_threads.workerUDPThreadSend,
                                     OperativeUDPThreadSend)

    def _test_udp_send_message_udp_available(self):
        AMP = MagicMock(return_value=True)
        self.create_settings_file()
        connect_info = get_data_local_file(settings_test_file)
        gsi = GroundStationInterface(connect_info, 'Vigo', AMP)
        test_threads = Threads(settings_test_file, gsi)
        test_threads.runUDPThreadReceive()

        message = 'This is a test message'


    def test_udp_send_message_udp_not_available(self):
        """

        :return:
        """
        AMP = MagicMock(return_value=True)
        self.create_settings_file()
        connect_info = get_data_local_file(settings_test_file)
        gsi = GroundStationInterface(connect_info, 'Vigo', AMP)
        test_threads = Threads(settings_test_file, gsi)

        message = 'This is a test message'
        result = test_threads.UDPThreadSend(message)

        return self.assertFalse(result)

    def _test_udp_stop_thread_udp_socket_active(self):
        pass

    def _test_udp_stop_thread_udp_socket_inactive(self):
        pass

    # FIXME Needs a patch method for OperativeKISSThreadReceive
    # FIXME or a mocked serial port.
    def _test_kiss_class_thread_created(self):
        AMP = MagicMock(return_value=True)
        self.create_settings_file()
        connect_info = get_data_local_file(settings_test_file)
        gsi = GroundStationInterface(connect_info, 'Vigo', AMP)
        test_threads = Threads(settings_test_file, gsi)

        print test_threads.runKISSThreadReceive()

    def _test_kiss_send_message_serial_available(self):
        pass

    def _test_kiss_send_message_serial_unavailable(self):
        pass

    def _test_kiss_stop_serial_available(self):
        pass

    def _test_kiss_stop_serial_unavailable(self):
        pass

    # TODO The following tests will be implemented in TCP phase.
    def _test_tcp_class_thread_receive_created(self):
        pass

    def _test_tcp_class_thread_send_created(self):
        pass

    def _test_tcp_send_message_udp_available(self):
        pass

    def _test_tcp_send_message_udp_not_available(self):
        pass

    def _test_tcp_stop_thread_udp_socket_active(self):
        pass

    def _test_tcp_stop_thread_udp_socket_inactive(self):
        pass


if __name__ == "__main__":
    main()
