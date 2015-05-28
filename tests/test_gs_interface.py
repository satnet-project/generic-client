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
		self.cp = ClientProtocol(self.CONNECTION_INFO)

	@mock.patch('socket.socket')
	@mock.patch('serial.Serial')
	def test_GroundStationInterface_withSerial_openSerialNotUDP(self, mock_serial, mock_socket):
		# Only serial connection should be initialized
		gsi = GroundStationInterface(self.CONNECTION_INFO, self.cp)
		mock_serial.assert_called_once_with(self.CONNECTION_INFO['serialport'], self.CONNECTION_INFO['baudrate'])
		self.assertFalse(mock_socket.called)

	def test_GroundStationInterface_frameFromSerial_processFrame(self):
		frame = 'test_frame'

		gsi = GroundStationInterface(self.CONNECTION_INFO, self.cp)
		# Create mock of processFrame to avoid the need of an active server
		self.cp.processFrame = mock.Mock()
		
		# All frames should be processed by the method processFrame in a
		# ClientProtocl object
		gsi._frameFromSerialport(frame)
		self.cp.processFrame.assert_called_once_with(frame)


class TestUDPGroundStationInterface(unittest.TestCase):

	def setUp(self):
		self.CONNECTION_INFO = {}
		self.CONNECTION_INFO['connection'] = 'udp'
		self.CONNECTION_INFO['ip'] = '10.0.0.1'
		self.CONNECTION_INFO['udpport'] = '2000'

		# Start connection
		self.cp = ClientProtocol(self.CONNECTION_INFO)

	@mock.patch('socket.socket.bind')
	@mock.patch('serial.Serial')
	def test_GroundStationInterface_withUDP_openUDPNotSerial(self, mock_serial, mock_socket):
		# Only serial connection should be initialized
		gsi = GroundStationInterface(self.CONNECTION_INFO, self.cp)
		mock_socket.assert_called_once_with((self.CONNECTION_INFO['ip'], self.CONNECTION_INFO['udpport']))
		self.assertFalse(mock_serial.called)

	"""
	@mock.patch('socket.socket')		
	def test_GroundStationInterface_frameFromUDP_processFrame(self, mock_socket):
		frame = 'test_frame'

		gsi = GroundStationInterface(self.CONNECTION_INFO, self.cp)
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