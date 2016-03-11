# coding=utf-8
from Queue import Queue
from twisted.python import log
import misc

from PyQt4 import QtCore

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
        """ UDP send method.

        @param message: Frame to be sent through UDP socket.
        @return: A boolean pointing the routine successful.
        """
        if not self.workerUDPThreadSend:
            log.msg(
                '>>> No UDP Thread Send, dropping message, msg = ' + str(
                    message
                )
            )
            return False
        else:
            self.workerUDPThreadSend.send(message)
            return True

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

    # TODO Method to be implemented.
    def runTCPThreadReceive(self):
        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsFile='.settings')
        self.workerTCPThread = OperativeTCPThread(self.tcp_queue,
                                                  self.sendData,
                                                  self.TCPSignal,
                                                  self.CONNECTION_INFO)
        self.workerTCPThread.start()

    # TODO Method to be implemented.
    def runTCPThreadSend(self):
        pass

    # TODO Method to be implemented.
    def stopTCPThread(self):
        self.workerTCPThread.stop()

    def sendData(self, result):
        self.gsi._manageFrame(result)


class MessagesThread(QtCore.QThread):
    """
    A QObject (to be run in a QThread) which sits waiting for data to come
    through a Queue.Queue().
    It blocks until data is available, and one it has got something from the
    queue, it sends it to the "MainThread" by emitting a Qt Signal
    """
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self, queue, *args, **kwargs):
        """

        @param queue: queue object already created.
        @param args: Inhered, Not used
        @param kwargs: Inhered. Not used.
        @return: None.
        """
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.queue = queue

    @QtCore.pyqtSlot()
    def run(self):
        """

        @return:
        """
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)


class WriteStream(object):
    """
    Messages from standard output are save to a queue object.

    """
    def __init__(self, queue):
        """ Init method.

        @param queue: The queue created for register the text messages.
        @return: None.
        """
        self.queue = queue

    def write(self, text):
        """ Write method.
        Append a new element to the queue.

        @param text: Text string to be show in screen.
        @return: None
        """
        self.queue.put(text)

    # TODO Improve description
    def flush(self):
        """

        @return:
        """
        pass