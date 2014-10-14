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
from __future__ import unicode_literals
from zope.i18n import translate
from gs.content.email.base import GroupNotifierABC
from gs.profile.notify import MessageSender
from . import GSMessageFactory as _


class DigestOnNotifier(GroupNotifierABC):
    htmlTemplateName = 'gs-group-member-email-settings-digest-on.html'
    textTemplateName = 'gs-group-member-email-settings-digest-on.txt'

    def notify(self, userInfo):
        subject = _('digest-on-subject',
                    'Topic digests from ${groupName}',
                    mapping={'groupName': self.groupInfo.name})
        translatedSubject = translate(subject)
        text = self.textTemplate(userInfo=userInfo)
        html = self.htmlTemplate(userInfo=userInfo)

        sender = MessageSender(self.context, userInfo)
        sender.send_message(translatedSubject, text, html)
        self.reset_content_type()


class DigestOffNotifier(GroupNotifierABC):
    htmlTemplateName = 'gs-group-member-email-settings-digest-off.html'
    textTemplateName = 'gs-group-member-email-settings-digest-off.txt'

    def notify(self, userInfo):
        subject = _('digest-off-subject',
                    'One email per post from ${groupName}',
                    mapping={'groupName': self.groupInfo.name})
        translatedSubject = translate(subject)
        text = self.textTemplate(userInfo=userInfo)
        html = self.htmlTemplate(userInfo=userInfo)

        sender = MessageSender(self.context, userInfo)
        sender.send_message(translatedSubject, text, html)
        self.reset_content_type()
