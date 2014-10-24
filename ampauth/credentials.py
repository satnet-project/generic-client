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


# First of all we need to add satnet-release-1/WebServices to the path
# to import Django modules
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()) + "/WebServices")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

# Import your models for use in your script
from zope.interface import implements, Interface
from twisted.python import log
from twisted.cred import portal, checkers, credentials
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.protocols.amp import IBoxReceiver
from twisted.internet import reactor

from django.contrib.auth.models import User

from server_amp import SATNETServer


"""
Verifies the user credentials against the Django users DB.
"""


class DjangoAuthChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def _passwordMatch(self, matched, user):
        if matched:
            log.msg('User ' + user.username + ' -> correct password')
            return user
        else:
            raise UnauthorizedLogin('Incorrect password')

    def requestAvatarId(self, creds):
        try:
            user = User.objects.get(username=creds.username)
            d = defer.maybeDeferred(user.check_password,
                                    creds.password)
            d.addCallback(self._passwordMatch, user)
            return d
        except User.DoesNotExist:
            raise UnauthorizedLogin('Incorrect username')


class Realm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IBoxReceiver in interfaces:
            return (IBoxReceiver, SATNETServer(), lambda: None)
        raise NotImplementedError()
