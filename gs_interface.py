# coding=utf-8
from twisted.python import log
from PyQt4 import QtCore
import time
import os
from types import NoneType

from serial.serialutil import SerialException

from errors import WrongFormatNotification, FrameNotProcessed
from errors import ConnectionNotEnded, IOFileError, SerialPortUnreachable

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


class GroundStationInterface(object):
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
    AMP = None
    GS = None

    def __init__(self, CONNECTION_INFO, GS, AMP):
        self.CONNECTION_INFO = CONNECTION_INFO
        # self.AMP = None
        self.AMP = AMP
        self.GS = GS

    def _manageFrame(self, result):
        if self.AMP is not None:
            # FIXME
            if type(result) is str:
                result = bytearray(result)

            if type(result) != bytearray:
                raise WrongFormatNotification("Bad format frame")

            try:
                self.AMP._processframe(result)
                self._updateLocalFile(result)
            except:
                raise FrameNotProcessed('Error processing Frame')
        else:
            if type(result) is bytearray:
                self._updateLocalFile(result)
            else:
                # To-do Change error description
                raise WrongFormatNotification("Bad format frame")

    def _updateLocalFile(self, frame):

        frameprocessed = list(frame)
        frameprocessed = ":".join("{:02x}".format(c)
                                  for c in frameprocessed)

        filename = self.GS + "-" + time.strftime("%Y.%m.%d") + ".csv"

        with open(filename, "a+") as f:
            f.write(str(time.strftime("%Y.%m.%d-%H:%M:%S ")) + frameprocessed
                    + "\n")

        if os.path.exists(filename):
            log.msg("--------------------------------------------- " +
                    "Message saved to local file" +
                    " ---------------------------------------------")
            return True
        else:
            raise IOFileError('Record file not created')


    def clear_slots(self):
        try:
            self.AMP.end_connection()
            self.disconnectProtocol()
            return True
        except:
            log.msg("Connection not established")
            # FIX-ME Only must raises an error if the connection was unestablished.
            # raise ConnectionNotEnded('EndRemote call not completed')

    def connectProtocol(self, AMP):
        """

        @param AMP: Client protocol to which received frames will be sent to be
        processed.
        @return:
        """
        log.msg('Protocol connected to the GS')
        self.AMP = AMP

    # Removes the reference to the protocol object (self.AMP). It shall
    # be invocked when the connection to the SATNET server is lost.
    def disconnectProtocol(self):
        """
        Removes the reference to the protocol object (self.AMP). It shall
        be invocked when the connection to the SATNET server is lost.
        @return:
        """
        log.msg("Protocol disconnected from the GS")
        self.AMP = None


# Class associated to UDP protocol
class UDPThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        self.running = True
        try:
            self.doWork()
        except:
            pass

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
        self.running = True
        try:
            self.doWork()
        except:
            pass

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
        if str(self.CONNECTION_INFO['udpipreceive']) == 'localhost':
            self.CONNECTION_INFO['udpipreceive'] = ''
        if str(self.CONNECTION_INFO['udpipreceive']) == '127.0.0.1':
            self.CONNECTION_INFO['udpipreceive'] = ''

        server_address = (str(self.CONNECTION_INFO['udpipreceive']),
                          int(self.CONNECTION_INFO['udpportreceive']))

        from socket import socket, AF_INET, SOCK_DGRAM
        from socket import SOL_SOCKET, SO_REUSEADDR, SHUT_RD
        try:
            self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
            if str(self.CONNECTION_INFO['udpipreceive']) == '':
                self.CONNECTION_INFO['udpipreceive'] = '127.0.0.1'
            log.msg("Opening UDP socket ---> " + "Listening on " +
                    self.CONNECTION_INFO['udpipreceive'] + " port: " +
                    str(self.CONNECTION_INFO['udpportreceive']))
        except Exception as e:
            log.err('Error opening UPD socket')
            log.err(e)

        self.UDPSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.UDPSocket.bind(server_address)

        if self.UDPSignal:
            while True:
                frame, address = self.UDPSocket.recvfrom(4096)
                self.catchValue(frame, address)

    def catchValue(self, frame, address):
        log.msg("--------------------------------------------- " +
                "Message from UDP socket" + " -----------------" +
                "----------------------------")
        log.msg("--------------------------------" +
                " Received from ip: " + str(address[0]) +
                " port: " + str(address[1]) + " --------------" +
                "------------------")

        self.finished.emit(frame)

    def stop(self):
        self.UDPSocket.close()
        self.UDPSignal = False
        del self.UDPSocket

        try:
            log.msg("UDP socket, %s ,not closed" %(str(type(self.UDPSocket))))
        except AttributeError:
            log.msg("UDPSocket stopped.")
            self.running = False
            return True


class OperativeUDPThreadSend():

    def __init__(self, CONNECTION_INFO):
        if str(CONNECTION_INFO['udpipsend']) == 'localhost':
            CONNECTION_INFO['udpipsend'] = ''
        if str(CONNECTION_INFO['udpipsend']) == '127.0.0.1':
            CONNECTION_INFO['udpipsend'] = ''

        self.server_address = (str(CONNECTION_INFO['udpipsend']),
                               int(CONNECTION_INFO['udpportsend']))

        from socket import socket, AF_INET, SOCK_DGRAM
        try:
            self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
            log.msg("                                         Writing on " +
                    CONNECTION_INFO['udpipsend'] + " port: " +
                    str(CONNECTION_INFO['udpportsend']))
        except Exception as e:
            log.err('Error opening UPD socket')
            log.err(e)

    def send(self, message):
        self.UDPSocket.sendto(message, self.server_address)

    def stop(self):
        self.UDPSocket.close()
        del self.UDPSocket


class OperativeKISSThread(KISSThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, serialSignal, CONNECTION_INFO,
                 parent=None):
        KISSThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)
        self.serialSignal = serialSignal

        self.signal = QtCore.SIGNAL('signal')
        self.init_interface(CONNECTION_INFO)

    def init_interface(self, CONNECTION_INFO):
        # Opening port
        import logging
        import kiss
        import kiss.constants

        self.kissTNC = kiss.KISS(CONNECTION_INFO['serialport'],
                                 CONNECTION_INFO['baudrate'])
        # TODO The logging level is actually set to ERROR because KISS tries
        # TODO to show the frames using the log standard Python method.
        # TODO This raises a codification error.
        # TODO Implement a workaround or fork the entire KISS module.
        self.kissTNC.console_handler.setLevel(logging.ERROR)

        try:
            self.kissTNC.start()
            log.msg("Opening KISS socket ---> " + "Serial port: " +
                    CONNECTION_INFO['serialport'] + " baudrate: " +
                    str(CONNECTION_INFO['baudrate']))
        except SerialException:
            raise SerialPortUnreachable("The port couldn't be open")


    def doWork(self):
        """ Work thread method.

        @return: True if everything goes alright, false if read method can't
        be set.
        """
        if self.serialSignal:
            self.kissTNC.read(callback=self.catchValue)
            return True
        else:
            return False

    def catchValue(self, frame):
        """

        @param frame:
        @return:
        """
        log.msg("----------------------------------------------- " +
                "Message from Serial port" +
                " -----------------------------------------------")
        self.finished.emit(frame[1:])

    def stop(self):
        """ Stop thread method.
        Emits a log message follows by a del sentence which deletes the
        KISS socket.
        The class attribute running is set to False.

        @return: Nothing,
        """
        log.msg('Stopping serial port')
        del self.kissTNC
        self.running = False

    def send(self, message):
        """ Send message method.
        Tries to send a frame through the formerly created KISS socket.

        @param message: A frame coded in a bytearray way.
        @return: None if the message is properly send and a
        SerialPortUnreachable exception if anything is wrong.
        """
        try:
            self.kissTNC.write(message)
            return True
        except AttributeError:
            raise SerialPortUnreachable('The serial port is unreachable')