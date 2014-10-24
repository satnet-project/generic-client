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


from twisted.internet.protocol import ServerFactory
from twisted.protocols.amp import AMP
from twisted.cred.credentials import UsernamePassword
from twisted.protocols.amp import IBoxReceiver
from twisted.python import log
from twisted.protocols.policies import TimeoutMixin

from commands import PasswordLogin
from twisted.cred.error import UnauthorizedLogin


class CredReceiver(AMP, TimeoutMixin):

    """
    Integration between AMP and L{twisted.cred}. This class is only intended
    to be used for credentials purposes. The specific SATNET protocol will be
    implemented in L{SATNETServer} (see server_amp.py).

    :ivar portal: 
        The L{Portal} against which login will be performed.  This is
        expected to be set by the factory which creates instances of this
        class.
    :type portal:
        L{Portal}

    :ivar logout: 
        C{None} or a no-argument callable.  This is set to the logout object
        returned by L{Portal.login} and is set while an avatar is logged in.

    :ivar sUsername:
        Each protocol belongs to a User. This field represents User.username
    :type sUsername:
        L{String}

    :ivar iTimeOut:
        The duration of the session timeout in seconds. After this time the user
        will be automagically disconnected.
    :type iTimeOut:
        L{int}
    """

    portal = None
    logout = None
    sUsername = 'NOT_AUTHENTICATED'
    iTimeOut = 300  # seconds
    iSlotEndCallId = None

    def connectionMade(self):
        self.setTimeout(self.iTimeOut)
        super(CredReceiver, self).connectionMade()

    def dataReceived(self, data):
        log.msg(self.sUsername + ' session timeout reset')
        self.resetTimeout()
        super(CredReceiver, self).dataReceived(data)

    def timeoutConnection(self):
        log.err('Session timeout expired')
        self.transport.abortConnection()

    def connectionLost(self, reason):
        # If the client has been added to active_protocols and/or to
        # active_connections
        if self.sUsername != 'NOT_AUTHENTICATED':
            # Remove from active protocols
            self.factory.active_protocols.pop(self.sUsername)
            if self.iSlotEndCallId is not None:
                self.iSlotEndCallId.cancel()
        log.err(reason.getErrorMessage())
        log.msg('Active clients: ' + str(len(self.factory.active_protocols)))
        # divided by 2 because the dictionary is doubly linked
        log.msg(
            'Active connections: ' + str(len(self.factory.active_connections) / 2))
        self.setTimeout(None)  # Cancel the pending timeout
        self.transport.loseConnection()
        super(CredReceiver, self).connectionLost(reason)

    def passwordLogin(self, sUsername, sPassword):
        """
        Generate a new challenge for the given username.
        """

        if self.factory.active_protocols.get(sUsername):
            log.err('Client already logged in')
            raise UnauthorizedLogin('Client already logged in')

        d = self.portal.login(
            UsernamePassword(sUsername, sPassword), None, IBoxReceiver)

        def cbLoggedIn((interface, avatar, logout)):
            self.sUsername = sUsername
            self.logout = logout
            self.boxReceiver = avatar
            self.boxReceiver.startReceivingBoxes(self.boxSender)
            # Pass to the SATNET server information of the active users.
            # If the next two lines were removed, only the authentication
            # server would have that information.
            avatar.factory = self.factory
            avatar.credProto = self
            avatar.sUsername = sUsername
            self.factory.active_protocols[sUsername] = avatar
            log.msg('Connection made')
            log.msg(
                'Active clients: ' + str(len(self.factory.active_protocols)))

            return {'bAuthenticated': True}
        d.addCallback(cbLoggedIn)
        return d
    PasswordLogin.responder(passwordLogin)


class CredAMPServerFactory(ServerFactory):

    """
    Server factory useful for creating L{CredReceiver} and L{SATNETServer} instances.

    This factory takes care of associating a L{Portal} with the L{CredReceiver}
    instances it creates. If the login is succesfully achieved, a L{SATNETServer}
    instance is also created.

    :ivar portal: 
        The portal which will be used by L{CredReceiver} instances
        created by this factory.
    :type portal:
        L{Portal}

    :ivar active_protocols:
        A dictionary containing a reference to all active protocols (clients).
        The dictionary keys are the client usernames and the corresponding values
        are the protocol instances
    :type active_protocols:
        L{Dictionary}

    :ivar active_connections:
        A dictionary containing a reference to all active protocols (clients).
        The dictionary is doubly linked so the keys are the whether the GS clients 
        or the SC clients and the values are the remote client usernames
    :type active_connections:
        L{Dictionary}        
    """

    protocol = CredReceiver
    active_protocols = {}
    active_connections = {}

    def __init__(self, portal):
        self.portal = portal

    def buildProtocol(self, addr):
        proto = ServerFactory.buildProtocol(self, addr)
        proto.portal = self.portal
        return proto
