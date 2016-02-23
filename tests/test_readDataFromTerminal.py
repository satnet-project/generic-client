# coding=utf-8
import unittest
import sys

from os import path
from PyQt4 import QtGui

from twisted.python import log
from mock import patch

sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))
import misc

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


class TestReadDataFromTerminal(unittest.TestCase):

    """
    No arguments passed at script startup.
    """
    def test_noArgumentsGiven(self):
        argumentsDict = misc.noArguments()

        arguments = ['username', 'slot', 'connection', 'serialport', 'baudrate',
                     'udpipsend', 'udpportsend', 'udpipreceive', 'udpportreceive']
        for i in range(len(arguments)):
            self.assertEquals(argumentsDict[arguments[i]],
                              '', "argumentsDict values are not null.")

    """
    Some arguments are initialized at script startup.
    """
    def test_ArgumentsGiven(self):
        testargs = ["client_amp.py", "-g", "-n", "crespo", "-t",
                    "2", "-c", "serial", "-s", "/dev/ttyS1",
                    "-b", "115200"]
        with patch.object(sys, 'argv', testargs):
            argumentsDict = misc.readArguments(testargs)

        descriptors = ['username', 'slot', 'baudrate', 'serialport',
                       'connection']

        for i in range(len(descriptors)):
            self.assertIsInstance(argumentsDict[(descriptors[i])], str,
                                  "Dict value is not a string object")

    def setUp(self):
        log.msg('starting tests')

    def teardrown(self):
        pass
