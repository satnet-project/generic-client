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

from unittest import TestCase

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from twisted.python import log

from ampauth.errors import BadCredentials
from rpcrequests import Satnet_RPC

"""
Tengo que 
Tengo que utilizar el objeto ClientProtocol.


"""

class CredentialsChecker(unittest.TestCase):

    def setUp(self):
        log.startLogging(sys.stdout)

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Setting username")

        return True

    """
    Send a correct frame
    """
    def test_CorrectFrame(self):

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Running CorrectFrame test")

        """
        Mock object.
        """
        _manageFrame = mock.Mock()
        GroundStationInterface.AMP = True

        @mock.patch('__main__.Satnet_RPC')
        def Satnet_RPC(self, sUsername, sPassword, debug=True):
            return True

        self.rpc = Satnet_RPC('xabi.crespo', mockUserGoodCredentials.password,\
         debug=True)

        log.msg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GoodCrendentials test ok!")

    # """
    # Send an incorrect frame
    # """
    # def test_BadFrame(self):

    #     log.msg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Running BadFrame test")

    #     """
    #     Mock object.
    #     """
    #     mockUserBadUsername = mock.Mock()
    #     mockUserBadUsername.username = 'wrongUser'
    #     mockUserBadUsername.password = 'pwd4django'

    #     @mock.patch('__main__.Satnet_RPC')
    #     def Satnet_RPC(self, sUsername, sPassword, debug=True):
    #         raise BadCredentials("Incorrect username")    

    #     log.msg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> BadUsername test ok!")

    #     return self.assertRaisesRegexp(BadCredentials, 'Incorrect username',\
    #      Satnet_RPC, mockUserBadUsername.username, mockUserBadUsername.password,\
    #       debug=True)


if __name__ == '__main__':

    unittest.main()  