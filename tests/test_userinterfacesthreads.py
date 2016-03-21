# coding=utf-8
import os
import sys
from mock import patch, MagicMock, Mock
from unittest import TestCase, main


from PySide import QtGui

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))
from client_ui import SatNetUI
from client_amp import Client
from threads import Threads
from misc import get_data_local_file
from gs_interface import GroundStationInterface, OperativeUDPThreadReceive
from gs_interface import OperativeUDPThreadSend
from client_amp import ClientProtocol


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



    @patch('__main__.OperativeUDPThreadReceive')
    def mockclientamp(OperativeUDPThreadReceive):
        """

        :return:
        """
        return True

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
    def _test_udp_class_thread_receive_created(self):
        """

        :return:
        """
        #OperativeUDPThreadReceive = Mock()

        AMP = MagicMock(return_value=True)
        #OperativeUDPThreadReceive = MagicMock(return_value=True)
        self.create_settings_file()
        connect_info = get_data_local_file('.settings')
        gsi = GroundStationInterface(connect_info, 'Vigo', AMP)

        with patch('__main__.OperativeUDPThreadReceive') as MockClass:
            instance = MockClass.return_value
            instance.method.return_value = True
            test_threads = Threads(connect_info, gsi)


            test_threads.runUDPThreadReceive()

        # print OperativeUDPThreadReceive.call_count


        # test_threads.stopUDPThreadReceive()

        # print OperativeUDPThreadReceive.call_count

        """
        return self.assertIsInstance(test_threads.workerUDPThreadReceive,
                                     OperativeUDPThreadReceive)
        """

    def test_udp_class_thread_send_created(self):
        """

        :return:
        """
        AMP = MagicMock(return_value=True)
        self.create_settings_file()
        connect_info = get_data_local_file('.settings')
        gsi = GroundStationInterface(connect_info, 'Vigo', AMP)
        test_threads = Threads(connect_info, gsi)

        test_threads.runUDPThreadSend()

        return self.assertIsInstance(test_threads.workerUDPThreadSend,
                                     OperativeUDPThreadSend)


if __name__ == "__main__":
    main()
