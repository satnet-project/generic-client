# coding=utf-8
import os
import sys
from mock import patch, MagicMock
from unittest import TestCase, main

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))
from gs_interface import UDPThread, KISSThread
from errors import UDPSocketUnreachable, SerialPortUnreachable


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


class TestThreadsOperationParentClasses(TestCase):

    # app = QtGui.QApplication(sys.argv)

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
        self.create_settings_file()

    def tearDown(self):
        os.remove('.settings')

    @patch.object(UDPThread, 'doWork')
    def test_init_udp_thread_run_called_ok(self, doWork):
        """

        :param doWork:
        :return:
        """
        test_threads = UDPThread()
        test_threads.run()

        return self.assertIs(int(doWork.call_count), 1)

    @patch.object(UDPThread, 'doWork', side_effect=Exception)
    def test_init_udp_thread_run_called_error(self, doWork):
        """

        :param doWork:
        :return:
        """
        test_threads = UDPThread()

        return self.assertRaises(UDPSocketUnreachable, test_threads.run)

    @patch.object(KISSThread, 'doWork')
    def test_init_kiss_thread_run_called_ok(self, doWork):
        """

        :param doWork:
        :return:
        """
        test_threads = KISSThread()
        test_threads.run()

        return self.assertIs(int(doWork.call_count), 1)

    @patch.object(KISSThread, 'doWork', side_effect=Exception)
    def test_init_kiss_thread_run_called_error(self, doWork):
        """

        :param doWork:
        :return:
        """
        test_threads = KISSThread()

        return self.assertRaises(SerialPortUnreachable, test_threads.run)

if __name__ == "__main__":
    main()