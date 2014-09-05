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
from zope.cachedescriptors.property import Lazy
from gs.group.list.command import CommandResult, CommandABC
from gs.group.member.base import user_member_of_group
from gs.group.member.email.base.interfaces import IGroupEmailUser
from .audit import (SettingsAuditor, DIGEST, DIGEST_COMMAND, EMAIL,
                    EMAIL_COMMAND)
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
        addr = self.get_addr(email)
        userInfo = self.get_userInfo(addr)
        if ((len(components) == 2) and (userInfo is not None)
           and user_member_of_group(userInfo, self.group)):
                subcommand = components[1].lower()
                if (subcommand in ('on', 'off')):
                    retval = CommandResult.commandStop
                    auditor = SettingsAuditor(self.context, userInfo,
                                              userInfo,  # Editing self
                                              self.groupInfo)
                    if subcommand == 'on':
                        auditor.info(DIGEST_COMMAND, addr)
                        self.digest_on(userInfo)
                        auditor.info(DIGEST)
                        notifier = DigestOnNotifier(self.group, request)
                    else:  # 'off'
                        auditor.info(EMAIL_COMMAND, addr)
                        self.digest_off(userInfo)
                        auditor.info(EMAIL)
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

    @staticmethod
    def get_addr(email):
        retval = parseaddr(email['From'])[1]
        return retval

    def get_userInfo(self, addr):
        'Get the userInfo from the ``From`` in the email message'
        retval = None
        sr = self.group.site_root()
        u = sr.acl_users.get_userByEmail(addr)
        if u:
            retval = createObject('groupserver.UserFromId', self.group,
                                  u.getId())
        return retval

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.group)
        return retval

    def get_groupEmailUser(self, userInfo):
        retval = getMultiAdapter((userInfo, self.groupInfo),
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
