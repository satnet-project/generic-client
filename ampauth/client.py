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


from twisted.python import log
from twisted.cred.credentials import IUsernamePassword
from commands import *
from twisted.cred.error import UnauthorizedLogin
from twisted.internet.defer import fail


class UnhandledCredentials(Exception):

    """
    L{login} was passed a credentials object which did not provide a 
    recognized credentials interface.
    """


def login(client, credentials):
    """
    Begin the authentication process by asking the server to verify the 
    user credentials using the given L{AMP} instance. The protocol must 
    be connected to a server with responders for L{PasswordLogin}.

    :param client:
        A connected L{AMP} instance which will be used to issue remote 
        authentication commands.
    :type client:
        L{AMP}
    :param credentials: 
        An L{IUsernamePassword} object containing the user credentials 
        which will be send to the server.
    :type credentials:
        L{IUsernamePassword}

    :return: 
        A L{Deferred} which fires when authentication has succeeded or
        which fails with L{UnauthorizedLogin} if the server rejects the
        authentication attempt.
    :rtype:
        L{Deferred}
    """
    if not IUsernamePassword.providedBy(credentials):
        raise UnhandledCredentials()

    log.msg("Login attempt: " + credentials.username)
    d = client.callRemote(
        PasswordLogin, sUsername=credentials.username, sPassword=credentials.password)
    return d
