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
import time


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
            try:
                self.AMP._processframe(result)
            except Exception as e:
                log.err('Error processing frame')
                log.err(e)
        else:
            self._updateLocalFile(result)

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