# coding=utf-8
import sys
import misc
import time
import client_ui
import os.path

from Queue import Queue
from OpenSSL import SSL

from PyQt4 import QtGui, QtCore

from errors import WrongFormatNotification, IOFileError

from twisted.python import log
from twisted.internet import ssl
from twisted.internet import error

from twisted.internet.ssl import ClientContextFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.amp import AMP
from twisted.internet.defer import inlineCallbacks

from ampCommands import Login, StartRemote, NotifyMsg
from ampCommands import NotifyEvent, SendMsg, EndRemote

"""
   Copyright 2015, 2016 Samuel Góngora García
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


class ClientProtocol(AMP):
    """
    Client class
    """

    def __init__(self, CONNECTION_INFO, gsi, threads):
        """

        @param CONNECTION_INFO:
        @param gsi:
        @param threads:
        """
        super(ClientProtocol, self).__init__()
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi
        self.threads = threads

        # self.factory.protoInstance = self

    def connectionMade(self):
        """ Connection made method.
        @return:
        """
        self.user_login()
        self.gsi.connectProtocol(self)

        log.msg("Connection sucessful")

    def connectionLost(self, reason):
        """ Connection lost method.
        Override method.

        @param reason:
        @return:
        """
        log.msg("Connection lost")
        log.msg(reason)

    def connectionFailed(self, reason):
        """ Connection failed method.
        Override method.

        @param reason:
        @return:
        """
        log.msg("Connection failed")
        log.msg(reason)

    @inlineCallbacks
    def end_connection(self):
        """

        @return:
        """
        res = yield self.callRemote(EndRemote)
        log.msg(res)

    @inlineCallbacks
    def user_login(self):
        """

        @return:
        """
        res = yield self.callRemote(Login,
                                    sUsername=self.CONNECTION_INFO['username'],
                                    sPassword=self.CONNECTION_INFO['password']
                                    )



        if res['bAuthenticated'] is True:
            res = yield self.callRemote(StartRemote)
        elif res['bAuthenticated'] is False:
            log.msg('False')
        else:
            log.msg('No data')

    # To-do. Do we need a return connection?
    def vNotifyMsg(self, sMsg):
        log.msg(">>> NOTIFY MESSAGE invoked:")

        # TODO. Check message integrity.
        # TODO. Check IPs and ports plausibility.

        import base64
        sMsg = base64.b64decode(sMsg)

        if self.CONNECTION_INFO['connection'] == 'serial':
            sMsg = bytearray(sMsg)

            self.saveReceivedFrames(sMsg)

            frameprocessed = list(sMsg)
            frameprocessed = ":".join("{:02x}".format(c)
                                  for c in frameprocessed)
            sMsg = str(sMsg)

            log.msg(frameprocessed)
            log.msg(">>> Delivering message...")
            self.threads.KISSThreadSend(sMsg)

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'udp':
            sMsg = bytearray(sMsg)

            self.saveReceivedFrames(sMsg)
            log.msg(">>> Delivering message...")

            # Checks if the message has been delivered
            if self.threads.UDPThreadSend(sMsg):
                return {'bResult': True}
            else:
                return {'bResult': False}

        elif self.CONNECTION_INFO['connection'] == 'tcp':
            sMsg = bytearray(sMsg)

            self.saveReceivedFrames(sMsg)
            # To-do. Implement TCP callback.

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'none':
            sMsg = bytearray(sMsg)

            self.saveReceivedFrames(sMsg)

            return {'bResult': True}

    NotifyMsg.responder(vNotifyMsg)

    def _processframe(self, frame):
        """ Process frame method.

        @param frame: A frame coded in a byte array way.
        @return:
        """
        frameprocessed = []
        try:
            frameprocessed = list(frame)
        except TypeError:
            raise WrongFormatNotification('The frame has an unexpected format')
        frameprocessed = ":".join("{:02x}".format(c)
                                  for c in frameprocessed)

        log.msg("Received frame: ", frameprocessed)

        # Convert to base64 string
        import base64
        frame = base64.b64encode(frame)

        self.processFrame(frame)

    @inlineCallbacks
    def processFrame(self, frame):
        """

        @param frame: A frame coded in base64.
        @return:
        """
        try:
            # yield self.callRemote(SendMsg, sMsg=frameProcessed,
            yield self.callRemote(SendMsg, sMsg=frame,
                                  iTimestamp=misc.get_utc_timestamp())
        except Exception as e:
            log.err(e)
            log.err("Error")

    def saveReceivedFrames(self, frame):
        """ Save received frames method.

        @param frame: A frame coded in a byte array way
        @return: True.
        """
        try:
            frameprocessed = list(frame)
        except TypeError:
            raise WrongFormatNotification('The frame has an unexpected format')
        frameprocessed = ":".join("{:02x}".format(c)
                                  for c in frameprocessed)
        """
        if type(frame) is not bytearray:
            raise WrongFormatNotification('Frame is %s' %(type(frame)))
        """

        filename = ("Rec-frames-" +
                    self.CONNECTION_INFO['name'] +
                    "-" + time.strftime("%Y.%m.%d") + ".csv")

        with open(filename, "a+") as f:
            f.write(str(time.strftime("%Y.%m.%d-%H:%M:%S")) + ' ' +
                    frameprocessed + "\n")

        if os.path.exists(filename):
            return True
        else:
            raise IOFileError('Record file not created')

        log.msg('---- Message received saved to local file ----')

    def vNotifyEvent(self, iEvent, sDetails):
        """

        @param iEvent:
        @param sDetails:
        @return:
        """
        sDetails = None
        log.msg("(" + self.CONNECTION_INFO['username'] +
                ") --------- Notify Event ---------")
        if iEvent == NotifyEvent.SLOT_END:
            log.msg('Disconnection because the slot has ended')
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.REMOTE_DISCONNECTED:
            log.msg("Remote client has lost the connection")
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.END_REMOTE:
            log.msg("The remote client has closed the connection")
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.REMOTE_CONNECTED:
            log.msg("The remote client has just connected")

        return {}
    NotifyEvent.responder(vNotifyEvent)


class ClientReconnectFactory(ReconnectingClientFactory):
    """
    ReconnectingClientFactory inherited object class to handle
    the reconnection process.
    """
    def __init__(self, CONNECTION_INFO, gsi, threads):
        self.CONNECTION_INFO = CONNECTION_INFO

        self.maxRetries = int(self.CONNECTION_INFO['attempts'])
        self.gsi = gsi
        self.threads = threads
        import platform
        os = platform.linux_distribution()
        if os[0] == 'debian':
            self.ossystem = 'debian'
        else:
            self.ossystem = 'ubuntu'

    # Called when a connection has been started
    def startedConnecting(self, connector):
        if self.ossystem  == 'ubuntu':
            log.msg("Starting connection............................" +
                    "..............................................." +
                    ".........................................")
        elif self.ossystem == 'debian':
            log.msg("Starting connection............................" +
                    "..............................................." +
                    "...........................")

    def buildProtocol(self, addr):
        """ Override build protocol method
        Create an instance of a subclass of protocol
        @param addr:
        @return: ClientProtocol instance
        """
        if self.ossystem == 'debian':
            log.msg("Building protocol.............................." +
                    "..............................................." +
                    "...........")
        elif self.ossystem == 'ubuntu':
            log.msg("Building protocol.............................." +
                    "..............................................." +
                    ".........................")

        self.resetDelay()

        return ClientProtocol(self.CONNECTION_INFO, self.gsi,
                              self.threads)

    def clientConnectionLost(self, connector, reason):
        """ Override client connection lost method
        Called when and established connection is lost
        @param connector:
        @param reason:
        @return:
        """
        CONNECTION_INFO = misc.get_data_local_file(settingsFile='.settings')
        print CONNECTION_INFO['reconnection']


        """
        if self.CONNECTION_INFO['reconnection'] == 'yes':
            self.continueTrying = True
        elif self.CONNECTION_INFO['reconnection'] == 'no':
            self.continueTrying = None
        """

        log.msg('Lost connection. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionLost(self,
                                                       connector,
                                                       reason)

    # Called when a connection has failed to connect
    def clientConnectionFailed(self, connector, reason):
        """ Override client connection failed method
        Called when
        @param connector:
        @param reason:
        @return:
        """
        if self.CONNECTION_INFO['reconnection'] == 'yes':
            self.continueTrying = True
        elif self.CONNECTION_INFO['reconnection'] == 'no':
            self.continueTrying = None

        log.msg('Connection failed. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionFailed(self,
                                                         connector,
                                                         reason)


class CtxFactory(ClientContextFactory):

    def getContext(self):
        """

        @return:
        """
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)

        return ctx


class Client(object):
    """
    This class starts the client using the data provided by user interface.
    :ivar CONNECTION_INFO:
        This variable contains the following data: username, password,
        slot_id, connection (either 'serial' or 'udp'), serialport,
        baudrate, ip, port.
    :type CONNECTION_INFO:
        L{Dictionary}
    :ivar
    """
    def __init__(self, CONNECTION_INFO, gsi, threads):
        self.CONNECTION_INFO = CONNECTION_INFO
        self.gsi = gsi
        self.threads = threads

    def createconnection(self, test):
        """

        @param test:
        @return:
        """
        if test is False:
            from qtreactor import pyqt4reactor
            pyqt4reactor.install()

    def setconnection(self, test):
        """
        @param test:
        @return:
        """
        from twisted.internet import reactor
        reactor.connectSSL(str(self.CONNECTION_INFO['serverip']),
                           int(self.CONNECTION_INFO['serverport']),
                           ClientReconnectFactory(self.CONNECTION_INFO,
                                                  self.gsi,self.threads),
                           CtxFactory()
                           )

        try:
            reactor.run(installSignalHandlers=0)
        except error.ReactorAlreadyRunning:
            log.msg("Reactor already running")
        """
        if test is False:
            try:
                reactor.run(installSignalHandlers=0)
            except:
                pass
        """
        return True

    def destroyconnection(self):
        """

        @return:
        """
        from twisted.internet import reactor
        reactor.stop()
        log.msg("Reactor destroyed")


class WriteStream(object):
    """

    """
    def __init__(self, queue):
        """

        @param queue:
        @return:
        """
        self.queue = queue

    def write(self, text):
        """

        @param text:
        @return:
        """
        self.queue.put(text)

    def flush(self):
        """

        @return:
        """
        pass


class MyReceiver(QtCore.QThread):
    """
    A QObject (to be run in a QThread) which sits waiting for data to come
    through a Queue.Queue().
    It blocks until data is available, and one it has got something from the
    queue, it sends it to the "MainThread" by emitting a Qt Signal
    """
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self, queue, *args, **kwargs):
        """

        @param queue:
        @param args:
        @param kwargs:
        @return:
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


class ResultObj(QtCore.QObject):
    """

    """
    def __init__(self, val):
        """

        @param val:
        @return:
        """
        self.val = val


if __name__ == '__main__':

    textqueue = Queue()
    sys.stdout = WriteStream(textqueue)

    log.startLogging(sys.stdout)
    log.msg('------------------------------------------------ ' +
            'SATNet - Generic client' +
            ' ------------------------------------------------')

    argumentsdict = misc.checkarguments(sysargvdict=sys.argv)

    qapp = QtGui.QApplication(sys.argv)
    app = client_ui.SatNetUI(argumentsdict=argumentsdict)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    app.show()

    my_receiver = MyReceiver(textqueue)
    my_receiver.mysignal.connect(app.append_text)
    my_receiver.start()

    sys.exit(qapp.exec_())
