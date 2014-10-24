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
from twisted.cred.error import UnauthorizedLogin


class PasswordLogin(amp.Command):

    """
    Command to authenticate an user.  The server response is a boolean
    granting or not the access to the client.

    :param sUsername:
        Client username for the SATNET network
    :type sUsername:
        String
    :param sPassword:
        Plain-text client password for the SATNET network
    :type sPassword:
        String

    :returns bAuthenticated:
        True if the user has been granted access and L{UnauthorizedLogin}
        otherwise.
    :rtype:
        boolean or L{UnauthorizedLogin}
    """

    arguments = [('sUsername', amp.String()),
                 ('sPassword', amp.String())]
    response = [('bAuthenticated', amp.Boolean())]
    errors = {
        UnauthorizedLogin: 'UNAUTHORIZED_LOGIN',
        NotImplementedError: 'NOT_IMPLEMENTED_ERROR'}
