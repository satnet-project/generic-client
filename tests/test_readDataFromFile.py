# coding=utf-8
import unittest
import sys

from os import path
from PyQt4 import QtGui

from twisted.python import log

sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))
from client_amp import SATNetGUI

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


class TestReadDataFromFile(unittest.TestCase):

    def test_loadParametersCorrectly(self):
        log.msg("To implement.")
        # Load parameters
        # Check return value

    def test_loadParametersIncorrectly(self):
        log.msg("To implement.")
        # Load parameters
        # Check return error

    def setUp(self):
        # Must initialize a QWidget object which contains the
        # load parameters method.
        argumentsDict = {}
        arguments = ['username', 'password', 'slot', 'connection',
                     'serialPort', 'baudRate', 'UDPIp', 'UDPPort']
        for i in range(len(arguments)):
            argumentsDict[arguments[i]] = ""


if __name__ == '__main__':
    unittest.main()
