# coding=utf-8
"""
   Copyright 2015 Xabier Crespo Álvarez

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


class BadCredentials(Exception):

    """
    One of the following situations may raise this error:
        1. Incorrect username
        2. Incorrect password
    """


class UnauthorizedLogin(Exception):

    """
    One of the following situations may raise this error:
        1. Client already logged in
    """


class SlotErrorNotification(Exception):

    """
    One of the following situations may raise this error:
        1. Slot not operational yet
        2. Multiple slots with the same ID
        3. Slot not reserved yet
        4. Slot not assigned to the invoking user
    """


class RemoteClientNotification(Exception):

    """
    One of the following situations may raise this error:
        1. Remote user not connected yet
        2. Remote user and invoking user coincide
            (i.e. MCC and GSS are the same)
    """


class WrongFormatNotification(Exception):

    """
    One of the following situations may raise this error:
        1. The actual frame has an incorrect format
    """

class IOFileError(Exception):

    """
    One of the following situations may raise this error:
        1. Some file hasn't been created
    """

class FrameNotProcessed(Exception):

    """
    One of the following situations may raise this error:
        1. Some error processing the frames
    """

class ConnectionNotEnded(Exception):

    """
    One of the following situations may raise this error:
        1. The connection has a failure and couldn't be ended
    """

class SettingsCorrupted(Exception):

    """
    One of the following situations may raise this error:
        1. The file doesn't have some fields.
    """

class SerialPortUnreachable(Exception):

    """
    One of the following situations may raise this error:
        1. The selected serial port is already open.
        2. The selected serial port is unreachable.
    """
