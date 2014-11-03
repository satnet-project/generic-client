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


from twisted.protocols import amp
from errors import *

"""
Commandes implemented by the N-server which will be invoked by a
G- or M- clients.
"""


class StartRemote(amp.Command):
    arguments = [('iSlotId', amp.Integer())]
    response = [('iResult', amp.Integer())]
    errors = {
        SlotErrorNotification: 'SLOT_ERROR_NOTIFICATION'}
    """
    Invoked when a client wants to connect to an N-server. This shall be called
    right after invoking login method.
    
    :param iSlotId:
        ID number of the slot which should have been previously reserved through
        the web interface.
    :type iSlotId:
        L{int}

    :returns iResult:
        Raises an error if the slot is not available yet or if it isn't assigned to 
        the calling client. Otherwise, it may return one of the following codes:

        (0) REMOTE_READY: the remote client is already connected to the server
        (-1) CLIENTS_COINCIDE: the remote client is the same as the calling client
        (-2) REMOTE_NOT_CONNECTED: indicates if the the remote client is not connected

        In case that any of the previous cases are detected, the slotId is returned.
    :rtype:
        int or L{SlotNotAvailable}
    """
    # Remote client ready
    REMOTE_READY = 0
    # Both MCC and GSS belong to the same client
    CLIENTS_COINCIDE = -1
    # Remote user not connected yet
    REMOTE_NOT_CONNECTED = -2


class EndRemote(amp.Command):
    arguments = []
    requiresAnswer = False
    """
    Invoked by a client whenever this one wants to finalize the remote operation.
    """


class SendMsg(amp.Command):
    arguments = [('sMsg', amp.String()),
                 ('iDopplerShift', amp.Integer()), ('sTimestamp', amp.String())]
    requiresAnswer = False
    """
    Invoked when a client wants to send a message to a remote entity. To use it, the 
    command StartRemote shall be invoked first.
    
    :param sMsg:
        String containing the message
    :type sMsg:
        L{String}
    :param iDopplerShift:
        Integer indicating the Doppler shift in kHz
    :type iDopplerShift:
        L{int}
    :param sTimestamp:
        String indicating the UTC timestamp at reception
    :type sTimestamp:
        L{String}    
    """

"""
Commandes implemented by G- or M- clients which will be invoked
by a N-server.
"""


class NotifyEvent(amp.Command):
    arguments = [('iEvent', amp.Integer()),
                 ('sDetails', amp.String(optional=True))]
    requiresAnswer = False
    """
    Used to inform a client about an event in the network. 
    
    :param iEvent:
        Code indicating the event.There are three cases:

        (-1) REMOTE_DISCONNECTED: notifies when the remote client has been disconnected
        and it is not receiving the messages.
        (-2) SLOT_END: notifies both clients about the slot end
        (-3) END_REMOTE: notifies a client that the remote has finished the connection
        (-4) REMOTE_CONNECTED: notifies a client when the remote has just connected
    :type iEvent:
        int

    :param sDetails:
        Details of the event. If it is REMOTE_CONNECTED this parameter is equal to 
        the username of the remote client. Otherwise the parameter is None

    :type sDetails:
        L{String} or None        
    """
    # Remote user not connected
    REMOTE_DISCONNECTED = -1
    # Both MCC and GSS belong to the same client
    SLOT_END = -2
    # Remote client finished connection
    END_REMOTE = -3
    # Remote client finished connection
    REMOTE_CONNECTED = -4


class NotifyMsg(amp.Command):
    arguments = [('sMsg', amp.String())]
    requiresAnswer = False
    """
    Used to send a message to a remote client.
    
    :param sMsg:
        Remote client identification number
    :type sMsg:
        L{String}
    """
