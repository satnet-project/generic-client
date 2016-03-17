# coding=utf-8
import os
import sys
import pty
import base64
import subprocess
from mock import patch

from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport
from twisted.internet.protocol import Factory
from twisted.protocols.amp import AMP

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "..")))
from ampCommands import NotifyMsg
from client_amp import ClientProtocol
from gs_interface import GroundStationInterface
from threads import Threads
from PySide import QtGui
from errors import SerialPortUnreachable

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


class MockFactory(Factory):
    pass


class TestClientProtocolReceiveFrame(TestCase):

    def setUp(self):
        CONNECTION_INFO = {'username': 'satnet_admin', 'password': 'pass', 'udpipsend': '172.19.51.145',
                           'baudrate': '500000', 'name': 'Universidade de Vigo', 'parameters': 'yes',
                           'tcpportsend': '1234', 'tcpipsend': '127.0.0.1', 'udpipreceive': '127.0.0.1',
                           'attempts': '10', 'serverip': '172.19.51.143', 'serialport': '/dev/ttyUSB0',
                           'tcpportreceive': 4321, 'connection': 'udp', 'udpportreceive': 57008,
                           'serverport': 25345, 'reconnection': 'no', 'udpportsend': '57009',
                           'tcpipreceive': '127.0.0.1'}

        GS = 'VigoTest'

        gsi = GroundStationInterface(CONNECTION_INFO, GS, AMP)
        threads = object

        self.sp = ClientProtocol(CONNECTION_INFO, gsi, threads)
        self.sp.factory = MockFactory()
        self.transport = StringTransport()
        self.sp.makeConnection(self.transport)

        self.transport.protocol = self.sp

        self.correct_frame = ("00:82:a0:00:00:53:45:52:50:2d:42:30:91:1d:1b:03:" +
                             "8d:0b:5c:03:02:28:01:9c:01:ab:02:4c:02:98:01:da:" +
                             "02:40:00:00:00:10:0a:46:58:10:00:c4:9d:cb:a2:21:39")

        self.wrongFrame = 9

    def tearDown(self):
        pass

    def test_client_receive_right_string(self):
        """ Client receives right frame.
        As NotityMsg returns a deferred it is need an addCallback method.
        @return: A deferred.
        """

        d = self.sp.callRemote(NotifyMsg, sMsg=self.correct_frame)
        d.addCallback(lambda res : self.assertTrue(res['bResult']))

    def test_client_receive_wrong_string(self):
        """ Client receives wrong frame.f
        NotifyMsg requires a string object for the transport. A different kind
        of object raises a TypeError exception.
        @return: An assertRaises method which checks the TypeError raise.
        """

        return self.assertRaises(TypeError, self.sp.callRemote,
                                 NotifyMsg, sMsg=self.wrongFrame)


class TestNotifyMsgSendMessageBack(TestCase):

    app = QtGui.QApplication(sys.argv)

    def mocked_open_kiss_interface(self, threads):
        threads.runKISSThreadReceive()

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

    def create_virtual_serial_port(self):
        outport = '/dev/ttyUSB0'
        inport = '/dev/ttyUSB1'
        cmd=['/usr/bin/socat','-d','-d','PTY,link=%s,raw,echo=1'%inport,
             'PTY,link=%s,raw,echo=1'%outport]
        self.proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

    def setUp(self):
        self.CONNECTION_INFO = {'username': 'satnet_admin', 'password': 'pass',
                                'udpipsend': '127',
                                'baudrate': '500000',
                                'name': 'Universidade de Vigo',
                                'parameters': 'yes', 'tcpportsend': '1234',
                                'tcpipsend': '127',
                                'udpipreceive': '127.0.0.1','attempts': '10',
                                'serverip': '172.19.51.143',
                                'serialport': 'self.s_name',
                                'tcpportreceive': 4321, 'connection': 'udp',
                                'udpportreceive': 57008, 'serverport': 25345,
                                'reconnection': 'no', 'udpportsend': '57009',
                                'tcpipreceive': '127.0.0.1'}

        self.correct_frame = bytearray(
            b"0082a00000534552502d4230911d1b038d0b5c030228")
        self.correct_frame = base64.b64encode(self.correct_frame)

    def tearDown(self):
        """ Tear down method.
        Between each test the settings configuration file must be remove.
        @return: Nothing.
        """
        os.remove('.settings')

    # FIXME Altought pty opens a serial port the connection it can't be open
    # FIXME http://stackoverflow.com/questions/2291772/virtual-serial-device-in-python
    def _test_serial_connection_selected_with_port_available(self):
        """ Serial connection selected with port available

        @return: Must return a True value.
        """
        self.create_virtual_serial_port()
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)
        self.create_settings_file()
        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'serial'
        self.mocked_open_interface_kiss(threads)

        # Lastest version of PySerial can't handle pseudo serial ports
        # https://github.com/pyserial/pyserial/issues/76

        master, slave = pty.openpty()
        s_name = os.ttyname(slave)

        self.CONNECTION_INFO['serialport'] = s_name
        serialconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correct_frame)

        return self.assertTrue(serialconnectionresponse['bResult'])

    # FIXME Altought self.sp.vNotitfyMsg raises the correct Exception the
    # FIXME self.assserRaises statement didn't catch it.
    # TODO Open issue.
    def _test_serial_connection_selected_without_port_available(self):
        """ Serial connection selected without any port available.
        Tries to established a serial connection though an unavailable
        serial port. Must raises a SerialException error.
        @return: An assertRaises method.
        """
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)
        self.create_settings_file()
        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'serial'
        self.mocked_open_interface_kiss(threads)

        self.assertRaises(SerialPortUnreachable,
                          self.sp.vNotifyMsg,
                          self.correct_frame)

    # FIXME Protocol doesn't check ips and ports.
    @patch.object(ClientProtocol, 'saveReceivedFrames')
    def _test_udp_connection_reachable(self, saveReceivedFrames):
        """ UDP connection can be reached.
        Inits a new connection using the threads methods. Should return a
        dict statement.

        @param saveReceivedFrames:
        @return:
        """
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)
        self.create_settings_file()
        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'udp'

        udpconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correct_frame)

        return self.assertTrue(udpconnectionresponse['bResult']), \
               self.assertTrue(saveReceivedFrames.called)

    # FIXME Protocol doesn't check ips and ports.
    @patch.object(ClientProtocol, 'saveReceivedFrames')
    def _test_udp_connection_unreachable(self, saveReceivedFrames):
        """ UDP connection can't be reached.

        @param saveReceivedFrames:
        @return:
        """
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)
        self.create_settings_file()
        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'udp'

        udpconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correct_frame)

        return self.assertFalse(udpconnectionresponse['bResult'])

    # TODO Complete description
    @patch.object(ClientProtocol, 'saveReceivedFrames')
    def test_tcp_connection_reachable(self, saveREceivedFrames):
        """

        @param saveREceivedFrames:
        @return:
        """
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)
        self.create_settings_file()
        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'tcp'

        tcpconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correct_frame)

        return self.assertTrue(tcpconnectionresponse['bResult']), \
               self.assertTrue(saveREceivedFrames.called)

    @patch.object(ClientProtocol, 'saveReceivedFrames')
    def test_no_connection_selected(self, saveReceivedFrames):
        """ No connection selected method.
        Store the received message.

        @param saveReceivedFrames: Method patched for test reasons.
        @return:
        """
        GS = 'VigoTest'
        gsi = GroundStationInterface(self.CONNECTION_INFO, GS, AMP)
        self.create_settings_file()
        threads = Threads(self.CONNECTION_INFO, gsi)
        self.sp = ClientProtocol(self.CONNECTION_INFO, gsi, threads)
        self.CONNECTION_INFO['connection'] = 'none'

        noneconnectionresponse = self.sp.vNotifyMsg(sMsg=self.correct_frame)

        return self.assertTrue(noneconnectionresponse['bResult']), \
               self.assertTrue(saveReceivedFrames.called)
