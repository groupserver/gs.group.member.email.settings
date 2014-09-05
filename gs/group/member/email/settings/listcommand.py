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
from gs.group.member.base import user_member_of_group
from gs.group.member.email.base.interfaces import IGroupEmailUser
from .notifier import (DigestOnNotifier, DigestOffNotifier)


class DigestCommand(CommandABC):
    'The ``digest`` command, which has two flags: ``on`` or ``off``.'

    def process(self, email, request):
        'Process the email command ``digest``'
        components = self.get_command_components(email)
        if components[0] != 'digest':
            m = 'Not a digest command: {0}'.format(email['Subject'])
            raise ValueError(m)

        retval = CommandResult.notACommand
        userInfo = self.get_userInfo(email)
        if ((len(components) == 2) and (userInfo is not None)
           and user_member_of_group(userInfo, self.group)):
                subcommand = components[1].lower()
                if (subcommand in ('on', 'off')):
                    retval = CommandResult.commandStop
                    if subcommand == 'on':
                        self.digest_on(userInfo)
                        notifier = DigestOnNotifier(self.group, request)
                    else:  # 'off'
                        self.digest_off(userInfo)
                        notifier = DigestOffNotifier(self.group, request)
                    assert notifier, 'notifier not set.'
                    notifier.notify(userInfo)
        # --=mpj17=-- If there is no extra parameter to "digest", or there
        # is no user for the From address in the email, or the user lacks
        # group membership then the message will be treated as a *normal*
        # *email*. This will almost certainly result in a "Not a member"
        # email going out, unless self.group is a support group. Confused?
        # Welcome to reality.
        assert isinstance(retval, CommandResult), \
            'retval not a command result'
        return retval

    def get_userInfo(self, email):
        'Get the userInfo from the ``From`` in the email message'
        retval = None

        addr = parseaddr(email['From'])[1]
        sr = self.group.site_root()
        u = sr.acl_users.get_userByEmail(addr)
        if u:
            retval = createObject('groupserver.UserFromId', self.group,
                                  u.getId())
        return retval

    def get_groupEmailUser(self, userInfo):
        groupInfo = createObject('groupserver.GroupInfo', self.group)
        retval = getMultiAdapter((userInfo, groupInfo),
                                 IGroupEmailUser, context=self.group)
        return retval

    def digest_on(self, userInfo):
        'Turn the digest on for the sender of the command'
        geu = self.get_groupEmailUser(userInfo)
        if geu:
            # TODO: Audit here
            geu.set_digest()

    def digest_off(self, userInfo):
        'Turn the digest on for the sender of the command'
        geu = self.get_groupEmailUser(userInfo)
        if geu:
            # TODO: Audit here
            geu.set_default_delivery()
