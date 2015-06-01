# coding=utf-8
"""
   Copyright 2014 Xabier Crespo Álvarez

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
    Xabier Crespo Álvarez (xabicrespog@gmail.com)
"""
__author__ = 'xabicrespog@gmail.com'


import unittest, mock, kiss
from client_amp import ClientProtocol
from gs_interface import GroundStationInterface


class TestSerialGroundStationInterface(unittest.TestCase):

	def setUp(self):
		self.CONNECTION_INFO = {}
		self.CONNECTION_INFO['connection'] = 'serial'
		self.CONNECTION_INFO['serialport'] = '/dev/ttyS0'
		self.CONNECTION_INFO['baudrate'] = '115200'

		# Start connection
		self.cp = ClientProtocol(self.CONNECTION_INFO, self)

	@mock.patch('socket.socket')
	@mock.patch('serial.Serial')
	def test_GroundStationInterface_withSerial_openSerialNotUDP(self, mock_serial, mock_socket):
		# Only serial connection should be initialized
		gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo", self.cp)

		mock_serial.assert_called_once_with(self.CONNECTION_INFO['serialport'], self.CONNECTION_INFO['baudrate'])
		self.assertFalse(mock_socket.called)

	def test_GroundStationInterface_frameFromSerial_processFrame(self):
		frame = 'test_frame'

		gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo", self.cp)

		# Create mock of processFrame to avoid the need of an active server
		self.cp.processFrame = mock.Mock()
		
		# All frames should be processed by the method processFrame in a
		# ClientProtocl object
		gsi._frameFromSerialport(frame)
		self.cp.processFrame.assert_called_once_with(frame)

	def test_GroundStationInterface_frameFromSerialNoConnection_writeToFile(self):
		frame = 'test_frame'

		gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo")

		# When the connection to the server is lost the protocol object is removed
		self.cp = None
		gsi._updateLocalFile = mock.Mock()

		# All frames should be processed saved to a local file
		gsi._frameFromSerialport(frame)
		gsi._updateLocalFile.assert_called_once_with(frame)


class TestUDPGroundStationInterface(unittest.TestCase):

	def setUp(self):
		self.CONNECTION_INFO = {}
		self.CONNECTION_INFO['connection'] = 'udp'
		self.CONNECTION_INFO['ip'] = '10.0.0.1'
		self.CONNECTION_INFO['udpport'] = '2000'

		# Start connection
		self.cp = ClientProtocol(self.CONNECTION_INFO, self)

	@mock.patch('socket.socket.bind')
	@mock.patch('serial.Serial')
	def test_GroundStationInterface_withUDP_openUDPNotSerial(self, mock_serial, mock_socket):
		# Only serial connection should be initialized
		gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo", self.cp)

		mock_socket.assert_called_once_with((self.CONNECTION_INFO['ip'], self.CONNECTION_INFO['udpport']))
		self.assertFalse(mock_serial.called)

	"""
	@mock.patch('socket.socket')		
	def test_GroundStationInterface_frameFromUDP_processFrame(self, mock_socket):
		frame = 'test_frame'

		gsi = GroundStationInterface(self.CONNECTION_INFO, self.cp, "Vigo")

		# Create mock of processFrame to avoid the need of an active server
		self.cp.processFrame = mock.Mock()
		
		# All frames should be processed by the method processFrame in a
		# ClientProtocl object
		socket = mock_socket.return_value

		socket.recvfrom.return_value = (frame, None)
		gsi._frameFromUDPSocket()

		self.cp.processFrame.assert_called_once_with(frame)
	"""
	
	if __name__ == '__main__':
		unittest.main()