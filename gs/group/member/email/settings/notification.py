# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2015 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals, print_function
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from gs.content.email.base import (GroupEmail, TextMixin)
UTF8 = 'utf-8'


class DigestOnHTML(GroupEmail):
    'The notification to the member that he or she is on Digest mode.'

    def __init__(self, group, request):
        super(DigestOnHTML, self).__init__(group, request)
        self.group = group

    def get_support_email(self, user):
        subj = 'Topic digest'
        uu = '{}{}'.format(self.siteInfo.url, user.url)
        msg = 'Hello,\n\nI sent a "digest on" email to {group} '\
              'and...\n\n--\nThese links may help you:\n  '\
              'Group          {url}\n  Me             {userUrl}\n'
        body = msg.format(group=self.groupInfo.name, url=self.groupInfo.url,
                          userUrl=uu)
        retval = self.mailto(self.siteInfo.get_support_email(), subj, body)
        return retval

    @Lazy
    def listAddress(self):
        emailList = createObject('groupserver.MailingListInfo', self.group)
        retval = emailList.get_property('mailto', '@')
        return retval

    @Lazy
    def digestOff(self):
        subject = 'digest off'
        b = 'Please set me to one email per post for {0}\n<{1}>'
        body = b.format(self.groupInfo.name, self.groupInfo.url)
        retval = self.mailto(self.listAddress, subject, body)
        return retval


class DigestOnTXT(DigestOnHTML, TextMixin):

    def __init__(self, group, request):
        super(DigestOnTXT, self).__init__(group, request)
        filename = 'digest-on-{0}-{1}.txt'.format(self.siteInfo.id,
                                                  self.groupInfo.id)
        self.set_header(filename)


# And off


class DigestOffHTML(DigestOnHTML):
    'The notification to the member that he or she is one email per post.'

    def __init__(self, group, request):
        super(DigestOffHTML, self).__init__(group, request)
        self.group = group

    @Lazy
    def digestOn(self):
        subject = 'digest on'
        r = 'mailto:{to}?subject={subj}'
        retval = r.format(to=self.listAddress, subj=subject)
        return retval

    def get_support_email(self, user):
        subj = 'Topic digest'
        uu = '{}{}'.format(self.siteInfo.url, user.url)
        msg = 'Hello,\n\nI sent a "digest off" email to {group} '\
              'and...\n\n--\nThese links may help you:\n  '\
              'Group          {url}\n  Me             {userUrl}\n'
        body = msg.format(group=self.groupInfo.name, url=self.groupInfo.url,
                          userUrl=uu)
        retval = self.mailto(self.siteInfo.get_support_email(), subj, body)
        return retval


class DigestOffTXT(DigestOffHTML, TextMixin):

    def __init__(self, group, request):
        super(DigestOffTXT, self).__init__(group, request)
        filename = 'digest-off-{0}-{1}.txt'.format(self.siteInfo.id,
                                                   self.groupInfo.id)
        self.set_header(filename)
