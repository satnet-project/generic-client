# coding=utf-8
"""
   Copyright 2015 Samuel Góngora García

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


import sys
import os
import unittest
import mock
import time

from twisted.python import log
from unittest import TestCase

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gs_interface import GroundStationInterface
from errors import WrongFormatNotification
from client_amp import ClientProtocol
import errors

from twisted.protocols.amp import AMP


class CredentialsChecker(unittest.TestCase):

    def mock_processframe(self, AMP_self, frame):
        CONNECTION_INFO = {}
        gsi = object

        log.msg("antes de clientprotocol")
        ClientProtocol(CONNECTION_INFO, gsi)._processframe(frame)
        log.msg("despues de clientprotocol")

    def mock_callremote(self, Send, sMsg, iTimestamp):
        log.msg("holaaa")

    def setUp(self):
        log.startLogging(sys.stdout)
        log.msg("")

        self.amp = AMP()

        return True

    """
    Send a correct frame without connection

    """
    def test_AMPnotPresentCorrectFrame(self):
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPnotPresentCorrectFrame test")

        frame = 'Frame'
        CONNECTION_INFO = {}
        GS = 'Vigo'
        self.amp = None

        gsi = GroundStationInterface(CONNECTION_INFO, GS, self.amp)
        gsi._manageFrame(frame)

        assert os.path.exists("ESEO-" + GS + "-" +\
         time.strftime("%Y.%m.%d") + ".csv") == 1
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMP not present - Local file created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPnotPresentCorrectFrame test OK")

    """
    Send a correct frame with connection
    """
    def _test_AMPPresentCorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPpresentCorrectFrame test")

        frame = 'Frame'
        CONNECTION_INFO = {}
        GS = 'Vigo'
        self.amp = mock.Mock()
        self.amp._processframe = mock.MagicMock(side_effect=self.mock_processframe)
        self.amp.callremote = mock.MagicMock(side_effect=self.mock_callremote)

        gsi = GroundStationInterface(CONNECTION_INFO, GS, self.amp)._manageFrame(frame)

    """
    Send an incorrect frame without connection
    """
    def test_AMPnotPresentIncorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPnotPresentIncorrectFrame test")

        frame = 1234
        CONNECTION_INFO = {}
        GS = 'Vigo'
        self.amp = None

        gsi = GroundStationInterface(CONNECTION_INFO, GS, self.amp)

        self.assertRaisesRegexp(WrongFormatNotification, "Bad format frame",\
          lambda: gsi._manageFrame(frame))
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMP present - Local file not created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPnotPresentIncorrectFrame test OK")

    """
    Send an incorrect frame with connection
    """
    def test_AMPPresentIncorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPPresentIncorrectFrame")

        frame = 1234
        CONNECTION_INFO = {}
        GS = 'Vigo'
        self.amp = mock.Mock()

        gsi = GroundStationInterface(CONNECTION_INFO, GS, self.amp)

        self.assertRaisesRegexp(Exception, "Bad format frame",\
          lambda: gsi._manageFrame(frame))
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Error - Local file not created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPPresentIncorrectFrame test OK")


if __name__ == '__main__':

    unittest.main()  