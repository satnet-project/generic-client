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


from twisted.python import log
import time


class GroundStationInterface():
    """
    This class contains the interface between the GS and the SATNET protocol.
    It supports either a UDP or a serial connection. In case the connection fails,
    received frames shall be stored in l{frameBuffer}.

    :ivar kissTNC:
        This object is in charge of communicating with a TNC which shall support
        KISS protocol.
    :type kissTNC:
        L{KISS}

    :ivar UDPSocket:
        This object is in charge of sending and receiving frames through an UDP 
        connection.
    :type UDPSocket:
        L{Socket}

    :ivar thread:
        This thread will constantly receive frames from the serial port or the 
        UDP socket.
    :type thread:
        L{Thread}

    :ivar frameBuffer:
        Contains the received frames that has not been sent to the server.
    :type frameBuffer:
        L{List}

    :ivar CONNECTION_INFO:
        This variable contains the following data: username, password, slot_id, 
        connection (either 'serial' or 'udp'), serialport, baudrate, ip, port.
    :type CONNECTION_INFO:
        L{Dictionary}

    :ivar AMP:
        Client protocol to which received frames will be sent to be processed. This
        object shall contain a method called 'processFrame'
    :type AMP:
        L{ClientProtocol}

    :ivar GS:
        Name of the GS that is receiving the data. It will be used to save the frames
        received to a local file in case of a connection failure.
    :type AMP:
        L{String}

    """

    kissTNC = None
    UDPSocket = None
    thread = None
    frameBuffer = None
    CONNECTION_INFO = {}
    AMP = None
    GS = None

    def __init__(self, CONNECTION_INFO, AMP, GS):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.AMP = AMP
        self.GS = GS

        if CONNECTION_INFO['connection'] == 'serial':
            self._open_serial()
        elif CONNECTION_INFO['connection'] == 'udp':
            self._open_socket()
        else:
            log.err('GS interface must be either "serial" or "udp"')

    def _open_serial(self):
        import kiss
        try:
            log.msg('Opening serial port (' + self.CONNECTION_INFO['serialport'] + ',' + self.CONNECTION_INFO['baudrate'] + ')')
            self.kissTNC = kiss.KISS(self.CONNECTION_INFO['serialport'], self.CONNECTION_INFO['baudrate'])
            self.kissTNC.start()  # inits the TNC, optionally passes KISS config flags.
            self.thread = threading.Thread(target=self.kissTNC.read, args=(self._frameFromSerialport,))
            self.thread.daemon = True # This thread will be close if the reactor stops
            self.thread.start()
        except:
            log.err('Serial port unavailable')

    def _open_socket(self):
        import socket
        try:
            log.msg('Opening UDP socket (' + self.CONNECTION_INFO['ip'] + ',' + self.CONNECTION_INFO['udpport'] + ')')
            self.UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            self.UDPSocket.bind((self.CONNECTION_INFO['ip'], self.CONNECTION_INFO['udpport']))
            self.thread = threading.Thread(target=self._frameFromUDPSocket)
            self.thread.daemon = True # This thread will be close if the reactor stops
            self.thread.start()
        except:
            log.err('UDP port unavailable')

    def _manageFrame(self, frame):
        if self.AMP is not None:
            self.AMP.processFrame(frame)
        else:
            self._updateLocalFile(frame)

    def _updateLocalFile(self, frame):
        filename = "ESEO-" + self.GS + "-" + time.strftime("%Y.%m.%d") + ".csv"
        with open(filename,"a+") as f:
            f.write(frame + ",")

    def _frameFromSerialport(self, frame):
        log.msg("--------- Message from Serial port ---------")
        self._manageFrame(frame)

    def _frameFromUDPSocket(self):
        log.msg("--------- Message from UDP socket ---------")        
        while True:
            frame, addr = self.UDPSocket.recvfrom(1024) # buffer size is 1024 bytes
            self._manageFrame(frame)