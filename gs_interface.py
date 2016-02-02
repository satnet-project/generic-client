# coding=utf-8
from twisted.python import log
from PyQt4 import QtCore
import time

from errors import WrongFormatNotification

"""
   Copyright 2014, 2015, 2016 Xabier Crespo Álvarez

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


class GroundStationInterface():
    """
    This class contains the interface between the GS and the SATNET protocol.
    It supports either a UDP or a serial connection. In case the connection to
    the SATNET server fails, received frames will be stored inside a csv file
    named ESEO-gs-yyy.mm.dd.csv.

    :ivar UDPSocket:
        This object is in charge of sending and receiving frames through an
        UDP connection.
    :type UDPSocket:
        L{Socket}

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
        Client protocol to which received frames will be sent to be processed.
        This object shall contain a method called 'processFrame'
    :type AMP:
        L{ClientProtocol}

    :ivar GS:
        Name of the GS that is receiving the data. It will be used to save the
        frames received to a local file in case of a connection failure.
    :type AMP:
        L{String}
    """

    UDPSocket = None
    TCPSocket = None
    frameBuffer = None
    CONNECTION_INFO = {}
    AMP = None
    GS = None

    def __init__(self, CONNECTION_INFO, GS, AMP):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.AMP = AMP
        self.GS = GS

    def _manageFrame(self, result):
        if self.AMP is not None:
            if type(result) != str:
                raise WrongFormatNotification("Bad format frame")

            try:
                # self.AMP._processframe(self, result)
                self.AMP._processframe(result)
            except Exception as e:
                log.err('Error processing frame')
                log.err(e)
        else:
            try:
                self._updateLocalFile(result)
            except TypeError:
                # To-do Change error description
                raise WrongFormatNotification("Bad format frame")

    def _updateLocalFile(self, frame):
        filename = "ESEO-" + self.GS + "-" + time.strftime("%Y.%m.%d") + ".csv"
        with open(filename, "a+") as f:
            f.write(frame + ",\n")

        log.msg('---- Message saved to local file ----')
    """
    :ivar AMP:
        Client protocol to which received frames will be sent to be
        processed. This object shall contain a method called 'processFrame'
    :type AMP:
        L{ClientProtocol}
    """
    def connectProtocol(self, AMP):
        log.msg('Protocol connected to the GS')
        self.AMP = AMP

    # Removes the reference to the protocol object (self.AMP). It shall
    # be invocked when the connection to the SATNET server is lost.
    def disconnectProtocol(self):
        log.msg("Protocol disconnected from the GS")
        self.AMP = None

    def test(self):
        log.msg("esto esto es un test")


# Class associated to UDP protocol
class UDPThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        self.running = True
        self.doWork()

    def doWork(self):
        return True

    def cleanUp(self):
        pass


# Class associated to TCP protocol
class TCPThread(QtCore.QThread):

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        self.doWork()

    def stop(self):
        log.msg('Stopping TCPSocket' +
                "..................................." +
                ".................................." +
                "..................................")
        self.TCPSocket.close()
        self.running = False

    def doWork(self):
        return True

    def cleanUp(self):
        pass


# Class associated to KISS protocol
class KISSThread(QtCore.QThread):

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        log.msg('Listening' + '.............................' +
                '................................................' +
                '.............................')

        self.running = True
        self.doWork()

    def doWork(self):
        return True

    def cleanUp(self):
        pass


class OperativeTCPThread(TCPThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, TCPSignal, CONNECTION_INFO,
                 parent=None):
        TCPThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)
        self.TCPSignal = TCPSignal

        server_address = (str(CONNECTION_INFO['tcpip']),
                          int(CONNECTION_INFO['tcpport']))

        from socket import socket, AF_INET, SOCK_STREAM
        try:
            log.msg("Opening TCP socket" + "...................." +
                    "..........................................." +
                    ".........................................")

            self.TCPSocket = socket(AF_INET, SOCK_STREAM)
        except Exception as e:
            log.err('Error opening TCP socket')
            log.err(e)

        try:
            self.TCPSocket.bind(server_address)
        except Exception as e:
            log.err('Error starting TCP protocol')
            log.err(e)

        log.msg('Listening on ' + str(self.CONNECTION_INFO['tcpip']) +
                " port: " + str(self.CONNECTION_INFO['tcpport']))
        try:
            self.running = True
            self.TCPSocket.listen(1)
            self.doWork(self.TCPSocket)

        except Exception as e:
            log.err('Error Listening TCP protocol')
            log.err(e)

    def doWork(self):
        if self.TCPSignal:
            while True:
                try:
                    con, address = self.TCPSocket.accept()
                    frame = con.recv(1024)
                    self.catchValue(frame, address)
                except Exception as e:
                    log.err('ErrorOperative TCP protocol')
                    log.err(e)

    def catchValue(self, frame, address):
        # self.finished.emit(ResultObj(frame))

        log.msg("----------------------------- " +
                "Message from TCP socket" +
                " -----------------------------")
        log.msg("------------------ Received from ip: " +
                str(address[0]) +
                " port: " +
                str(address[1]) + " ------------------")


class OperativeUDPThreadReceive(UDPThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, UDPSignal, CONNECTION_INFO,
                 parent=None):
        UDPThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)
        self.UDPSignal = UDPSignal
        self.CONNECTION_INFO = CONNECTION_INFO

    def doWork(self):
        log.msg('Listening on ' + self.CONNECTION_INFO['udpip'] +
                " port: " + str(self.CONNECTION_INFO['udpport']))

        if str(self.CONNECTION_INFO['udpip']) == 'localhost':
            self.CONNECTION_INFO['udpip'] = ''
        if str(self.CONNECTION_INFO['udpip']) == '127.0.0.1':
            self.CONNECTION_INFO['udpip'] = ''

        server_address = (str(self.CONNECTION_INFO['udpip']),
                          int(self.CONNECTION_INFO['udpport']))

        from socket import socket, AF_INET, SOCK_DGRAM
        try:
            log.msg("Opening UPD socket" + ".........................." +
                    '..........................................' +
                    '....................................')
            self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        except Exception as e:
            log.err('Error opening UPD socket')
            log.err(e)

        self.UDPSocket.bind(server_address)

        if self.UDPSignal:
            while True:
                frame, address = self.UDPSocket.recvfrom(4096)
                self.catchValue(frame, address)

    def catchValue(self, frame, address):
        # self.finished.emit(ResultObj(frame))
        log.msg("----------------------------------------------- " +
                "Message from UDP socket" + " -------------------" +
                "----------------------------")
        log.msg("--------------------------------" +
                " Received from ip: " + str(address[0]) +
                " port: " + str(address[1]) + " --------------" +
                "------------------")
        self.finished.emit(frame)

    def stop(self):
        log.msg('Stopping UDPSocket' + "........." +
                "..............................................." +
                "...............................................")
        self.UDPSocket.close()
        self.running = False


class OperativeUDPThreadSend(UDPThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, UDPSignal, CONNECTION_INFO,
                 parent=None):
        UDPThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)
        self.UDPSignal = UDPSignal
        self.CONNECTION_INFO = CONNECTION_INFO

    def doWork(self):
        log.msg("Writing on " + self.CONNECTION_INFO['udpip'] +
                " port: " + str(self.CONNECTION_INFO['udpport']))

        if str(self.CONNECTION_INFO['udpip']) == 'localhost':
            self.CONNECTION_INFO['udpip'] = ''
        if str(self.CONNECTION_INFO['udpip']) == '127.0.0.1':
            self.CONNECTION_INFO['udpip'] = ''

        server_address = (str(self.CONNECTION_INFO['udpip']),
                          45874)

        from socket import socket, AF_INET, SOCK_DGRAM
        try:
            log.msg("Opening UPD socket" + "....................." +
                    "............................................" +
                    ".......................................")
            self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        except Exception as e:
            log.err('Error opening UPD socket')
            log.err(e)

        server_address = (str(self.CONNECTION_INFO['udpip']),
                          45874)

        self.UDPSocket.bind(server_address)

        if self.UDPSignal:
            while True:
                self.UDPSocket.sendto('message', server_address)
                # self.catchValue(frame, address)

    """
    def catchValue(self, frame, address):
        # self.finished.emit(ResultObj(frame))
        log.msg("----------------------------------------------- " +
                "Message from UDP socket" + " -------------------" +
                "----------------------------")
        log.msg("--------------------------------" +
                " Received from ip: " + str(address[0]) +
                " port: " + str(address[1]) + " --------------" +
                "------------------")
        self.finished.emit(frame)

    def stop(self):
        log.msg('Stopping UDPSocket' + "........." +
                "..............................................." +
                "...............................................")
        self.UDPSocket.close()
        self.running = False
    """


class OperativeKISSThread(KISSThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, serialSignal, CONNECTION_INFO,
                 parent=None):
        KISSThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)
        self.serialSignal = serialSignal

        # Opening port
        import logging
        import kiss
        import kiss.constants
        try:
            log.msg("Opening serial port" + "...................." +
                    "............................................" +
                    "..........................................")

            self.kissTNC = kiss.KISS(CONNECTION_INFO['serialport'],
                                     CONNECTION_INFO['baudrate'])
            formatter = logging.Formatter('%(name)s - %(message)s')
            self.kissTNC.console_handler.setFormatter(formatter)

        except Exception as e:
            log.err('Error opening port')
            log.err(e)

        try:
            self.kissTNC.start()
        except Exception as e:
            log.err('Error starting KISS protocol')
            log.err(e)

    def doWork(self):
        if self.serialSignal:
            # Only needs to be initialized one time.
            self.kissTNC.read(callback=self.catchValue)

            return True

    def catchValue(self, frame):
        # self.finished.emit(ResultObj(frame))
        log.msg("--------------------------------------- " +
                "Message from Serial port" +
                " -------------------------------------")
        self.finished.emit(frame)

    def stop(self):
        log.msg('Stopping serial port')
        self.running = False
