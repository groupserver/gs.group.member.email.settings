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
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, getMultiAdapter
from gs.core import to_ascii
from gs.profile.notify import MessageSender
UTF8 = 'utf-8'


class DigestOnNotifier(object):
    htmlTemplateName = 'gs-group-member-email-settings-digest-on.html'
    textTemplateName = 'gs-group-member-email-settings-digest-on.txt'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        h = self.request.response.getHeader('Content-Type')
        self.oldContentType = to_ascii(h if h else 'text/html')

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.context)
        assert retval, 'Failed to create the GroupInfo from %s' % \
            self.context
        return retval

    @Lazy
    def htmlTemplate(self):
        retval = getMultiAdapter((self.context, self.request),
                                 name=self.htmlTemplateName)
        return retval

    @Lazy
    def textTemplate(self):
        retval = getMultiAdapter((self.context, self.request),
                                 name=self.textTemplateName)
        return retval

    def notify(self, userInfo):
        sender = MessageSender(self.context, userInfo)
        subject = 'Topic digests from {}'.format(self.groupInfo.name)
        text = self.textTemplate()
        html = self.htmlTemplate()
        sender.send_message(subject, text, html)

        self.request.response.setHeader(to_ascii('Content-Type'),
                                        to_ascii(self.oldContentType))


class DigestOffNotifier(DigestOnNotifier):
    htmlTemplateName = 'gs-group-member-email-settings-digest-off.html'
    textTemplateName = 'gs-group-member-email-settings-digest-off.txt'

    def notify(self, userInfo):
        sender = MessageSender(self.context, userInfo)
        subject = 'One email per post from {}'.format(self.groupInfo.name)
        text = self.textTemplate()
        html = self.htmlTemplate()
        sender.send_message(subject, text, html)

        self.request.response.setHeader(to_ascii('Content-Type'),
                                        to_ascii(self.oldContentType))
