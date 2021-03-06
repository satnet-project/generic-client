# coding=utf-8
from Queue import Queue
from twisted.python import log
import misc

from gs_interface import GroundStationInterface, OperativeUDPThreadReceive
from gs_interface import OperativeUDPThreadSend
from gs_interface import OperativeTCPThread, OperativeKISSThread


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


class Threads(object):

    workerUDPThreadSend = None

    def __init__(self, CONNECTION_INFO, gsi):
        self.UDPSignal = True
        self.serialSignal = True
        self.TCPSignal = True
        self.tcp_queue = Queue()
        self.udp_queue = Queue()
        self.serial_queue = Queue()
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')
        self.gsi = gsi

    def runUDPThreadReceive(self):
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')
        self.workerUDPThreadReceive = OperativeUDPThreadReceive(
            self.udp_queue, self.sendData, self.UDPSignal, self.CONNECTION_INFO
        )
        self.workerUDPThreadReceive.start()

    def stopUDPThreadReceive(self):
        self.workerUDPThreadReceive.stop()

    def runUDPThreadSend(self):
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')
        self.workerUDPThreadSend = OperativeUDPThreadSend(self.CONNECTION_INFO)

    def UDPThreadSend(self, message):
        if not self.workerUDPThreadSend:
            log.msg(
                '>>> No UDP Thread Send, dropping message, msg = ' + str(
                    message
                )
            )
        else:
            self.workerUDPThreadSend.send(message)

    def runKISSThreadReceive(self):
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')
        self.workerKISSThread = OperativeKISSThread(self.serial_queue,
                                                    self.sendData,
                                                    self.serialSignal,
                                                    self.CONNECTION_INFO)
        self.workerKISSThread.start()

    def stopKISSThread(self):
        self.workerKISSThread.stop()

    def KISSThreadSend(self, message):
        self.workerKISSThread.send(message)

    # To-do
    def runTCPThread(self):
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')
        self.workerTCPThread = OperativeTCPThread(self.tcp_queue,
                                                  self.sendData,
                                                  self.TCPSignal,
                                                  self.CONNECTION_INFO)
        self.workerTCPThread.start()

    # Stop TCP thread
    def stopTCPThread(self):
        self.workerTCPThread.stop()

    def sendData(self, result):
        self.gsi._manageFrame(result)