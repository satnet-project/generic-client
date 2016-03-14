# coding=utf-8
import client_ui
import sys
import os.path

from ampCommands import Login, StartRemote, NotifyMsg
from ampCommands import NotifyEvent, SendMsg, EndRemote
from base64 import b64encode, b64decode
from errors import WrongFormatNotification, IOFileError
from Queue import Queue
from misc import checkarguments, get_utc_timestamp, get_data_local_file
from OpenSSL import SSL
from PySide import QtGui
from threads import MessagesThread, WriteStream
from time import strftime
from twisted.python import log
from twisted.internet import ssl
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.ssl import ClientContextFactory
from twisted.protocols.amp import AMP

import os
import json
import logging.config


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
        """ Connection made method.
        @return:
        """
        self.user_login()
        self.gsi.connectProtocol(self)
        logging.info("Connection sucessful.")

    def connectionLost(self, reason):
        """ Connection lost method.
        Override method.

        @param reason:
        @return:
        """
        logging.info("Connection lost.")
        logging.debug(reason)

    def connectionFailed(self, reason):
        """ Connection failed method.
        Override method.

        @param reason:
        @return:
        """
        logging.info("Connection failed.")
        logging.debug(reason)

    @inlineCallbacks
    def end_connection(self):
        """

        @return:
        """
        res = yield self.callRemote(EndRemote)
        logging.debug(res)

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
            # res = yield self.callRemote(StartRemote)
            yield self.callRemote(StartRemote)
        elif res['bAuthenticated'] is False:
            logging.debug("Not authenticated")
        else:
            logging.debug(("Authenticated"))

    def vNotifyMsg(self, sMsg):
        """ Notify message from SatNet protocol.

        @param sMsg: A frame received from SatNet protocol,
        @return: A dictionary.
        """
        logging.debug(">>> NOTIFY MESSAGE invoked:")

        # TODO. Check message integrity.
        # TODO. Check IPs and ports plausibility.

        sMsg = b64decode(sMsg)
        sMsg = bytearray(sMsg)
        self.saveReceivedFrames(sMsg)

        if self.CONNECTION_INFO['connection'] == 'serial':
            frameprocessed = list(sMsg)
            frameprocessed = ":".join("{:02x}".format(c)
                                  for c in frameprocessed)
            sMsg = str(sMsg)

            # logging.debug(frameprocessed)
            logging.info(">>> Delivering message...")
            if self.threads.KISSThreadSend(sMsg):
                return {'bResult': True}
            else:
                return {'bResult': False}

        elif self.CONNECTION_INFO['connection'] == 'udp':
            logging.info(">>> Delivering message...")

            # Checks if the message has been delivered
            if self.threads.UDPThreadSend(sMsg):
                return {'bResult': True}
            else:
                return {'bResult': False}

        elif self.CONNECTION_INFO['connection'] == 'tcp':
            # TODO. Implement.
            return {'bResult': True}

        elif self.CONNECTION_INFO['connection'] == 'none':
            return {'bResult': True}

    NotifyMsg.responder(vNotifyMsg)

    def _processframe(self, frame):
        """ Process frame method.

        @param frame: A frame coded in a byte array way.
        @return: Nothing if everything is alright. A WrongFormatNotifiction
        exception if the frame cannot be processed.
        """
        try:
            frameprocessed = list(frame)
        except TypeError:
            raise WrongFormatNotification('The frame has an unexpected format')
        frameprocessed = ":".join("{:02x}".format(c)
                                  for c in frameprocessed)

        # logging.info("Received frame: ", frameprocessed)

        # Convert to base64 string
        frame = b64encode(frame)

        self.processFrame(frame)

    @inlineCallbacks
    def processFrame(self, frame):
        """

        @param frame: A frame coded in base64.
        @return:
        """
        try:
            yield self.callRemote(SendMsg, sMsg=frame,
                                  iTimestamp=get_utc_timestamp())
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
            logging.error("The frame has an unexpected format")
            raise WrongFormatNotification("The frame has an unexpected format")
        frameprocessed = ":".join("{:02x}".format(c)
                                  for c in frameprocessed)

        filename = ("Rec-frames-" +
                    self.CONNECTION_INFO['name'] +
                    "-" + strftime("%Y.%m.%d") + ".csv")

        with open(filename, "a+") as f:
            f.write(str(strftime("%Y.%m.%d-%H:%M:%S")) + ' ' +
                    frameprocessed + "\n")

        if os.path.exists(filename):
            logging.debug("---- Message received saved to local file ----")
            return True
        else:
            logging.error("Record file not created")
            raise IOFileError("Record file not created")

    def vNotifyEvent(self, iEvent, sDetails):
        """

        @param iEvent:
        @param sDetails:
        @return:
        """
        log.msg(sDetails)

        log.msg("(" + self.CONNECTION_INFO['username'] +
                ") --------- Notify Event ---------")
        if iEvent == NotifyEvent.SLOT_END:
            logging.info("Disconnection because the slot has ended")
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.REMOTE_DISCONNECTED:
            logging.info("Remote client has lost the connection")
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.END_REMOTE:
            logging.info("The remote client has closed the connection")
            self.callRemote(EndRemote)
        elif iEvent == NotifyEvent.REMOTE_CONNECTED:
            logging.info("The remote client has just connected")

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

    def buildProtocol(self, addr):
        """ Override build protocol method
        Create an instance of a subclass of protocol
        @param addr:
        @return: ClientProtocol instance
        """
        logging.debug("Building client protocol at %s" % addr )
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
        CONNECTION_INFO = get_data_local_file('.settings')

        if CONNECTION_INFO['reconnection'] == 'yes':
            self.continueTrying = True
        elif CONNECTION_INFO['reconnection'] == 'no':
            self.continueTrying = None

        logging.debug('Lost connection. Reason: %s' %(str(reason)))
        ReconnectingClientFactory.clientConnectionLost(self,
                                                       connector,
                                                       reason)

    def clientConnectionFailed(self, connector, reason):
        """ Override client connection failed method
        Called when a connection has failed to connect
        @param connector:
        @param reason:
        @return:
        """

        CONNECTION_INFO = get_data_local_file('.settings')

        if CONNECTION_INFO['reconnection'] == 'yes':
            self.continueTrying = True
        elif CONNECTION_INFO['reconnection'] == 'no':
            self.continueTrying = None

        logging.debug('Connection failed. Reason: %s' %(str(reason)))
        ReconnectingClientFactory.clientConnectionFailed(self,
                                                         connector,
                                                         reason)


class CtxFactory(ClientContextFactory):

    def __init__(self):
        pass

    def getContext(self):
        """

        @return:
        """
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)

        return ctx


# TODO Improve security?
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

        @param test: Useful flag for switch off pyqt4reactor installation
        during tests.
        @return: None
        """
        if test is False:
            from qtreactor import qtreactor_config
            qtreactor_config._instance.qtname = 'PySide'

            import qtreactor.pyside4reactor
            qtreactor.pyside4reactor.install()

    def setconnection(self, test):
        """
        @param test: Useful flag for switch off reactor installation during
        tests.
        @return: A boolean True if everything go alright.
        """
        from twisted.internet import reactor
        reactor.connectSSL(str(self.CONNECTION_INFO['serverip']),
                           int(self.CONNECTION_INFO['serverport']),
                           ClientReconnectFactory(self.CONNECTION_INFO,
                                                  self.gsi, self.threads),
                           CtxFactory()
                           )

        if test is False:
            if not reactor.running:
                reactor.run(installSignalHandlers=0)

        return True

    def destroyconnection(self):
        """ Destroy connection method.
        Stops the actual reactor instance. Emits a helpful message.

        @return: None.
        """
        from twisted.internet import reactor
        reactor.stop()
        logging.debug("Reactor destroyed")
        logging.shutdown()


def start_logging(level=None):
    log_settings = logging.getLogger()
    if level == 'DEBUG':
        log_settings.setLevel(logging.DEBUG)
    elif level == 'INFO':
        log_settings.setLevel(logging.INFO)
    elif level == 'ERROR':
        log_settings.setLevel(logging.ERROR)

    debug_log = logging.StreamHandler(sys.stdout)
    debug_log.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter('%(asctime)s - %(message)s')
    debug_log.setFormatter(debug_formatter)

    info_log = logging.FileHandler('info.log')
    info_log.setLevel(logging.INFO)
    info_formatter = logging.Formatter('%(asctime)s - %(message)s')
    info_log.setFormatter(info_formatter)

    error_log = logging.FileHandler('error.log')
    error_log.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %('
                                        'message)s')
    error_log.setFormatter(error_formatter)

    log_settings.addHandler(debug_log)
    log_settings.addHandler(info_log)
    log_settings.addHandler(error_log)

    logging.info('------------------------------------------------ ' +
                 'SATNet - Generic client' +
                 ' ------------------------------------------------')


if __name__ == '__main__':
    textqueue = Queue()
    # TODO Actually only standard messages are logged.
    # TODO Should we register standard error too?

    # TODO Create differente logger levels.

    argumentsdict = checkarguments(sysargv_dict=sys.argv)
    sys.stdout = WriteStream(textqueue)
    logging_level = argumentsdict['log_level']
    start_logging(level=logging_level)

    qapp = QtGui.QApplication(sys.argv)
    main_application = client_ui.SatNetUI(argumentsdict=argumentsdict)
    main_application.show()

    messages_receiver = MessagesThread(textqueue)
    messages_receiver.mysignal.connect(main_application.append_text)
    messages_receiver.start()

    sys.exit(qapp.exec_())
