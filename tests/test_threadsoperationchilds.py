# coding=utf-8
import os
import sys
from mock import patch, MagicMock, Mock
from unittest import TestCase, main
import Queue

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))
from gs_interface import OperativeUDPThreadReceive, OperativeUDPThreadSend
from errors import UDPSocketUnreachable, SerialPortUnreachable
from misc import get_data_local_file


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


class TestThreadsOperationChildClasses(TestCase):

    def callback(self, frame):
        print frame

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

    @patch.object(OperativeUDPThreadReceive, 'finished',
                  return_value=True)
    def _test_init_udp_thread_receive_run_called_ok(self, finished):
        """

        :param finished:
        :return:
        """
        queue = Queue
        frame = ''
        callback = self.callback(frame)
        UDPSignal = True
        connect_info = get_data_local_file('.settings')
        test_threads = OperativeUDPThreadReceive(queue, callback, UDPSignal,
                                                 connect_info)
        test_threads.doWork()

    @patch.object(OperativeUDPThreadReceive, 'finished',
                  return_value=True)
    def _test_init_udp_thread_receive_run_called_raise_exception(self,
                                                                finished):
        """

        :param doWork:
        :return:
        """
        queue = Queue
        frame = ''
        callback = self.callback(frame)
        UDPSignal = True
        connect_info = get_data_local_file('.settings')
        test_threads = OperativeUDPThreadReceive(queue, callback, UDPSignal,
                                                 connect_info)
        test_threads.doWork()

    @patch.object(OperativeUDPThreadReceive, 'finished',
                  return_value=True)
    def _test_udp_thread_receive_catch_value_ok(self, finished):
        """

        :return:
        """
        queue = Queue
        frame = ''
        callback = self.callback(frame)
        UDPSignal = True
        connect_info = get_data_local_file('.settings')
        test_threads = OperativeUDPThreadReceive(queue, callback, UDPSignal,
                                                 connect_info)

        test_frame = 'This is a test frame'
        test_address = ['localhost', 57008]

        test_threads.catchValue(test_frame, test_address)

    @patch.object(OperativeUDPThreadReceive, 'finished')
    def _test_udp_thread_receive_catch_value_raise_exception(self, finished):
        """

        :return:
        """
        finished.emit = MagicMock(side_effect=Exception)
        queue = Queue
        frame = ''
        callback = self.callback(frame)
        UDPSignal = True
        connect_info = get_data_local_file('.settings')
        test_threads = OperativeUDPThreadReceive(queue, callback, UDPSignal,
                                                 connect_info)

        test_frame = 'This is a test frame'
        test_address = ['localhost', 57008]

        return self.assertFalse(test_threads.catchValue(test_frame,
                                                        test_address))

    @patch.object(OperativeUDPThreadReceive, 'finished')
    def _test_stop_receive_udp_ok(self, finished):
        """

        :param finished:
        :return:
        """
        finished.emit = MagicMock(side_effect=Exception)
        queue = Queue
        frame = ''
        callback = self.callback(frame)
        UDPSignal = True
        connect_info = get_data_local_file('.settings')
        test_threads = OperativeUDPThreadReceive(queue, callback, UDPSignal,
                                                 connect_info)

        test_threads.UDPSocket = Mock()
        test_threads.UDPSocket.close = MagicMock(return_value=True)

        return self.assertTrue(test_threads.stop()), \
               self.assertFalse(test_threads.running)

    # TODO Implement
    def _test_stop_receive_udp_not_ok(self):
        pass

    def test_udp_thread_send_ok(self):
        """

        :return:
        """
        connect_info = get_data_local_file('.settings')
        test_threads = OperativeUDPThreadSend(connect_info)

        test_frame = 'This is a test frame'
        test_address = ['localhost', 57008]

        print test_threads.send(test_frame)

if __name__ == "__main__":
    main()