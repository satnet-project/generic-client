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

    def connectionMade(self):
        self.user_login()
        self.gsi.connectProtocol(self)

    def connectionLost(self, reason):
        log.msg("Connection lost")

    def connectionFailed(self, reason):
        log.msg("Connection failed")

    @inlineCallbacks
    def end_connection(self):
        res = yield self.callRemote(EndRemote)
        log.msg(res)

    @inlineCallbacks
    def user_login(self):
        res = yield self.callRemote(Login,
                                    sUsername=self.CONNECTION_INFO['username'],
                                    sPassword=self.CONNECTION_INFO['password'])

        if res['bAuthenticated'] is True:
            res = yield self.callRemote(StartRemote)
        elif res['bAuthenticated'] is False:
            log.msg('False')
        else:
            log.msg('No data')

    # To-do. Do we need a return connection?
    def vNotifyMsg(self, sMsg):
        log.msg(">>> NOTIFY MESSAGE invoked:")

        # To-do. Check message integrity.
        # To-do. Check IPs and ports plausibility.

        if self.CONNECTION_INFO['connection'] == 'serial':
            sMsg = bytearray(sMsg)
            del sMsg[:1]

            self.saveReceivedFrames(sMsg)

            import kiss
            self.kissTNC = kiss.KISS(self.CONNECTION_INFO['serialport'],
                                     self.CONNECTION_INFO['baudrate'])
            self.kissTNC.start()
            log.msg(">>> Delivering message...")
            self.kissTNC.write(sMsg)

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'udp':
            sMsg = bytearray(sMsg)
            del sMsg[:1]

            self.saveReceivedFrames(sMsg)
            log.msg(">>> Delivering message...")
            self.threads.UDPThreadSend(sMsg)

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'tcp':
            sMsg = bytearray(sMsg)
            del sMsg[:1]

            self.saveReceivedFrames(sMsg)
            # To-do. Implement TCP callback.

            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'none':
            sMsg = bytearray(sMsg)
            del sMsg[:1]

            self.saveReceivedFrames(sMsg)

            return {'bResult': True}

    NotifyMsg.responder(vNotifyMsg)

    # Method associated to frame processing.
    def _processframe(self, frame):
        frameprocessed = []
        frameprocessed = list(frame)
        frameprocessed = ":".join("{:02x}".format(ord(c))
                                  for c in frameprocessed)

        log.msg("Received frame: ", frameprocessed)

        self.processFrame(frame)

    @inlineCallbacks
    def processFrame(self, frame):
        try:
            # yield self.callRemote(SendMsg, sMsg=frameProcessed,
            yield self.callRemote(SendMsg, sMsg=frame,
                                  iTimestamp=misc.get_utc_timestamp())
        except Exception as e:
            log.err(e)
            log.err("Error")

    def saveReceivedFrames(self, frame):
        log.msg('---- Message received saved to local file ----')

        if type(frame) is not bytearray:
            raise WrongFormatNotification('Frame is %s' %(type(frame)))

        frame = bytearray(frame)
        del frame[:1]

        filename = ("RECEIVED-FRAMES-" +
                    self.CONNECTION_INFO['name'] +
                    "-" + time.strftime("%Y.%m.%d") + ".csv")

        with open(filename, "a+") as f:
            f.write(str(time.strftime("%Y.%m.%d-%H:%M:%S")) +
                    frame + "\n")


        if os.path.exists(filename):
            return True
        else:
            raise IOFileError('Record file not created')


    def vNotifyEvent(self, iEvent, sDetails):
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
        self.gsi = gsi
        self.threads = threads

    # Called when a connection has been started
    def startedConnecting(self, connector):
        log.msg("Starting connection............................" +
                "..............................................." +
                ".........................................")

    # Create an instance of a subclass of Protocol
    def buildProtocol(self, addr):
        log.msg("Building protocol.............................." +
                "..............................................." +
                ".........................")
        self.resetDelay()
        return ClientProtocol(self.CONNECTION_INFO, self.gsi,
                              self.threads)

    # Called when an established connection is lost
    def clientConnectionLost(self, connector, reason):
        if self.CONNECTION_INFO['reconnection'] == 'yes':
            self.continueTrying = True
        elif self.CONNECTION_INFO['reconnection'] == 'no':
            self.continueTrying = None

        log.msg('Lost connection. Reason: ', reason)
        ReconnectingClientFactory.clientConnectionLost(self,
                                                       connector,
                                                       reason)

    # Called when a connection has failed to connect
    def clientConnectionFailed(self, connector, reason):
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

    def createconnection(self):
        from qtreactor import pyqt4reactor
        pyqt4reactor.install()

    def setconnection(self):
        from twisted.internet import reactor
        reactor.connectSSL(str(self.CONNECTION_INFO['serverip']),
                           int(self.CONNECTION_INFO['serverport']),
                           ClientReconnectFactory(
                            self.CONNECTION_INFO,
                            self.gsi, self.threads),
                           CtxFactory())


        try:
            reactor.run(installSignalHandlers=0)
        except:
            pass

        return self.gsi

    def destroyconnection(self):
        from twisted.internet import reactor
        reactor.stop()
        log.msg("Reactor destroyed")

# Objects designed for output the information
class WriteStream(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass

#  A QObject (to be run in a QThread) which sits waiting
#  for data to come  through a Queue.Queue().
#  It blocks until data is available, and one it has got something from
#  the queue, it sends it to the "MainThread" by emitting a Qt Signal


class MyReceiver(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self, queue, *args, **kwargs):
        """

        @rtype: pyqtSlot
        """
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.queue = queue

    @QtCore.pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)


class ResultObj(QtCore.QObject):
    def __init__(self, val):
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
    app = client_ui.SATNetGUI(argumentsDict=argumentsdict)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    app.show()

    my_receiver = MyReceiver(textqueue)
    my_receiver.mysignal.connect(app.append_text)
    my_receiver.start()

    sys.exit(qapp.exec_())
