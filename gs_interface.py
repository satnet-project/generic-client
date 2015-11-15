# coding=utf-8
"""
   Copyright 2014, 2015 Xabier Crespo Álvarez

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
from PyQt4 import QtCore
import time

from errors import WrongFormatNotification


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
                self.AMP._processframe(self, result)
            except Exception as e:
                log.err('Error processing frame')
                log.err(e)
        else:
            try:
                self._updateLocalFile(result)
            except TypeError:
                raise WrongFormatNotification("Bad format frame")

    def _updateLocalFile(self, frame):
        log.msg('---- Saving message to local file ----')
        filename = "ESEO-" + self.GS + "-" + time.strftime("%Y.%m.%d") + ".csv"
        with open(filename,"a+") as f:
            f.write(frame + ",\n")

    # :ivar AMP:
    #     Client protocol to which received frames will be sent to be 
    #     processed. This object shall contain a method called 'processFrame'
    # :type AMP:
    #     L{ClientProtocol}    
    def connectProtocol(self, AMP):
        log.msg('Protocol connected to the GS')
        self.AMP = AMP

    # Removes the reference to the protocol object (self.AMP). It shall 
    # be invocked when the connection to the SATNET server is lost.
    def disconnectProtocol(self):
        log.msg('Protocol disconnected from the GS')   
        self.AMP = None


# Class associated to UDP protocol
class UDPThread(QtCore.QThread):
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)

        # Test!! To-do.

        self.CONNECTION_INFO = {'ip':'127.0.0.1', 'udpport':'5001'}
        server_address = (str(self.CONNECTION_INFO['ip']),\
         int(self.CONNECTION_INFO['udpport']))

        from socket import socket, AF_INET, SOCK_DGRAM
        try:
            log.msg("Opening UPD socket" + ".........................." +\
         '...........................' + '...........................' +\
          '........................')

            self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        except Exception as e:
            log.err('Error opening UPD socket')
            log.err(e)

        try:
            self.UDPSocket.bind(server_address)
        except Exception as e:
            log.err('Error starting UPD protocol')
            log.err(e)

    def run(self):
        log.msg('Listening on ' + str(self.CONNECTION_INFO['ip']) +\
         " port: " + str(self.CONNECTION_INFO['udpport']))
        self.running = True
        self.doWork(self.UDPSocket)
        # success = self.doWork(self.kissTNC)
        # self.emit(SIGNAL("readingPort( PyQt_PyObject )"), success )
    
    def stop(self):
        log.msg('Stopping UDPSocket' +\
         "..................................." +\
         "................................" +\
          "....................................")
        self.UDPSocket.close()
        self.running = False
    
    def doWork(self):
        return True
    
    def cleanUp(self):
        pass

# Class associated to TCP protocol
class TCPThread(QtCore.QThread):
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)

        self.CONNECTION_INFO = {'ip':'127.0.0.1', 'tcpport':'5001'}
        server_address = (str(self.CONNECTION_INFO['ip']),\
         int(self.CONNECTION_INFO['tcpport']))

        from socket import socket, AF_INET, SOCK_STREAM
        try:
            log.msg("Opening TCP socket" + ".........................." +\
         '...........................' + '...........................' +\
          '........................')

            self.TCPSocket = socket(AF_INET, SOCK_STREAM)
        except Exception as e:
            log.err('Error opening TCP socket')
            log.err(e)

        try:
            self.TCPSocket.bind(server_address)
        except Exception as e:
            log.err('Error starting TCP protocol')
            log.err(e)

    def run(self):
        
        log.msg('Listening on ' + str(self.CONNECTION_INFO['ip']) +\
         " port: " + str(self.CONNECTION_INFO['tcpport']))
        try:
            self.running = True
            self.TCPSocket.listen(1)
            self.doWork(self.TCPSocket)
            
        except Exception as e:
            log.err('Error Listening TCP protocol')
            log.err(e)
        # success = self.doWork(self.kissTNC)
        # self.emit(SIGNAL("readingPort( PyQt_PyObject )"), success )
    
    def stop(self):
        log.msg('Stopping TCPSocket' +\
         "..................................." +\
         "................................" +\
          "....................................")
        self.TCPSocket.close()
        self.running = False
    
    def doWork(self):
        return True
    
    def cleanUp(self):
        pass


# Class associated to KISS protocol
class KISSThread(QtCore.QThread):
    
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)

        # Opening port
        import logging
        import kiss
        import kiss.constants
        try:
            log.msg('Opening serial port' + '.............................' +\
             '................................................' +\
              '.............................')

            self.kissTNC = kiss.KISS('/dev/ttyS1', '9000')
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

    def run(self):
        log.msg('Listening')
        self.running = True
        self.doWork(self.kissTNC)
        # success = self.doWork(self.kissTNC)
        # self.emit(SIGNAL("readingPort( PyQt_PyObject )"), success )
    
    def stop(self):
        log.msg('Stopping serial port')
        self.running = False
    
    def doWork(self):
        return True
    
    def cleanUp(self):
        pass


class OperativeTCPThread(TCPThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, TCPSignal, parent = None):
        TCPThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)
        self.TCPSignal = TCPSignal
    
    def doWork(self, TCPSocket):
        if self.TCPSignal:
            while True:
                try:
                    con, address= TCPSocket.accept()
                    frame= con.recv(1024) # buffer size is 1024 bytes
                    self.catchValue(frame, address)
                except Exception as e:
                    log.err('ErrorOperative TCP protocol')
                    log.err(e)

    def catchValue(self, frame, address):
        # self.finished.emit(ResultObj(frame))

        log.msg("----------------------------- " + "Message from TCP socket" +\
         " -----------------------------")
        log.msg("------------------ Received from ip: " + str(address[0]) +\
         " port: " + str(address[1]) +  " ------------------")      
        self.finished.emit(frame)
    
    
class OperativeUDPThread(UDPThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, UDPSignal, parent = None):
        UDPThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)
        self.UDPSignal = UDPSignal
    
    def doWork(self, UDPSocket):
        if self.UDPSignal:
            while True:
                frame, address = UDPSocket.recvfrom(1024) # buffer size is 1024 bytes
                self.catchValue(frame, address)

    def catchValue(self, frame, address):
        # self.finished.emit(ResultObj(frame))

        log.msg("----------------------------- " + "Message from UDP socket" +\
         " -----------------------------")
        log.msg("------------------ Received from ip: " + str(address[0]) +\
         " port: " + str(address[1]) +  " ------------------")      
        self.finished.emit(frame)


class OperativeKISSThread(KISSThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, serialSignal, parent = None):
        KISSThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)
        self.serialSignal = serialSignal

    def doWork(self, kissTNC):
        if self.serialSignal:
            # Only needs to be initialized one time.
            kissTNC.read(callback=self.catchValue)
            return True

    def catchValue(self, frame):
        # self.finished.emit(ResultObj(frame))

        log.msg('---- Message from Serial port ----')
        self.finished.emit(frame)