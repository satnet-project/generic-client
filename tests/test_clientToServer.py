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

    def setUp(self):
        log.startLogging(sys.stdout)
        log.msg("")

        return True

    """
    Send a correct frame without connection

    """
    def test_AMPnotPresentCorrectFrame(self):
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPnotPresentCorrectFrame test")

        frame = 'Frame'
        CONNECTION_INFO = {}
        GS = 'Vigo'
        AMP = None

        gsi = GroundStationInterface(CONNECTION_INFO, GS, AMP)
        gsi._manageFrame(frame)

        assert os.path.exists("ESEO-" + GS + "-" +\
         time.strftime("%Y.%m.%d") + ".csv") == 1
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Local file created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPnotPresentCorrectFrame test OK")

    """
    Send a correct frame with connection
    """
    def _test_AMPPresentCorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPpresentCorrectFrame test")

        frame = 'Frame'
        CONNECTION_INFO = {}
        GS = 'Vigo'
        amp = AMP
        # AMP._processframe = self._test()
        # AMP._processframe = mock.MagicMock(side_effect=self._test(frame))

        # AMP._processframe = self.prueba(frame)

        gsi = GroundStationInterface(CONNECTION_INFO, GS, AMP)._manageFrame(frame)

        log.msg(AMP._processframe)

        ClientProtocol(CONNECTION_INFO, gsi)._processframe(frame)
        # ClientProtocol(CONNECTION_INFO, gsi).processframe(frame)

        """
        Falta hacer el mock de la funcion call
        """

    """
    Send an incorrect frame without connection
    """
    def test_AMPnotPresentIncorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPnotPresentIncorrectFrame test")

        frame = 1234
        CONNECTION_INFO = {}
        GS = 'Vigo'
        AMP = None

        gsi = GroundStationInterface(CONNECTION_INFO, GS, AMP)

        self.assertRaisesRegexp(WrongFormatNotification, "Bad format frame",\
          lambda: gsi._manageFrame(frame))
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Error - Local file not created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPnotPresentIncorrectFrame test OK")

    """
    Send an incorrect frame with connection

    El problema viene cuando procesa el frame que ve que no es una cadena de texto
    correcta. Introducir comparación de tipo de fichero.
    """
    def test_AMPPresentIncorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Running AMPPresentIncorrectFrame")

        frame = 1234
        CONNECTION_INFO = {}
        GS = 'Vigo'
        AMP = mock.Mock()

        gsi = GroundStationInterface(CONNECTION_INFO, GS, AMP)

        self.assertRaisesRegexp(Exception, "Bad format frame",\
          lambda: gsi._manageFrame(frame))
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> Error - Local file not created")
        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>> AMPPresentIncorrectFrame test OK")


if __name__ == '__main__':

    unittest.main()  