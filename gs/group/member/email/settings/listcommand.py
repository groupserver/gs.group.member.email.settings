# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
from email.utils import parseaddr
from zope.component import createObject, getMultiAdapter
from gs.group.list.command import CommandResult, CommandABC
from gs.group.member.email.base.interfaces import IGroupEmailUser


class DigestCommand(CommandABC):
    'The ``digest`` command, which has two flags: ``on`` or ``off``.'

    def process(self, email, request):
        'Process the email command ``digest``'
        components = self.get_command_components(email)
        if components[0] != 'digest':
            m = 'Not a digest command: {0}'.format(email['Subject'])
            raise ValueError(m)

        retval = CommandResult.notACommand
        if ((len(components) == 2) and (components[1] == 'on')):
            self.digest_on(email)
            # TODO: Send notification
            retval = CommandResult.commandStop
        elif ((len(components) == 2) and (components[1] == 'off')):
            self.digest_off(email)
            # TODO: Send notification
            retval = CommandResult.commandStop

        return retval

    def digest_on(self, email):
        'Turn the digest on for the sender of the command'
        geu = self.get_groupEmailUser(email)
        if geu:
            # TODO: Log here
            geu.set_digest()

    def digest_off(self, email):
        'Turn the digest on for the sender of the command'
        geu = self.get_groupEmailUser(email)
        if geu:
            # TODO: Log here
            geu.set_default_delivery()

    def get_groupEmailUser(self, email):
        retval = None

        addr = parseaddr(email['From'])[1]
        sr = self.group.site_root()
        u = sr.acl_users.get_userByEmail(addr)
        if u:
            userInfo = createObject('groupserver.UserFromId', self.group,
                                    u.getId())
            groupInfo = createObject('groupserver.GroupInfo', self.group)
            retval = getMultiAdapter((userInfo, groupInfo),
                                     IGroupEmailUser, context=self.group)
        return retval
