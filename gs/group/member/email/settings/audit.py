# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2010, 2011, 2012, 2013, 2014 OnlineGroups.net and
# Contributors.
#
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
from pytz import UTC
from datetime import datetime
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.component.interfaces import IFactory
from zope.interface import implementer, implementedBy
from gs.core import comma_comma_and
from Products.XWFCore.XWFUtils import munge_date
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, AuditQuery
from Products.GSAuditTrail.utils import event_id_from_data
SUBSYSTEM = 'gs.group.member.email.settings'
from logging import getLogger
log = getLogger(SUBSYSTEM)
UNKNOWN = '0'  # Unknown is always "0"
DIGEST = '1'
DIGEST_COMMAND = '2'
WEB_ONLY = '3'
# WEB_ONLY_COMMAND = '4'  # There is no web-only command... yet
EMAIL = '5'
EMAIL_COMMAND = '6'
ADDRESS_DEFAULT = '7'
ADDRESS_SPECIFIC = '8'


@implementer(IFactory)
class GroupEmailSettingsAuditEventFactory(object):
    """A Factory for group member email-settings events."""

    title = 'GroupServer Group Member Email Settings Audit Event Factory'
    description = 'Creates a GroupServer event auditor for changing the'\
                  'email settings'

    def __call__(self, context, event_id, code, date, userInfo,
                 instanceUserInfo, siteInfo, groupInfo, instanceDatum='',
                 supplementaryDatum='', subsystem=''):
        """Create an event"""
        assert subsystem == SUBSYSTEM, 'Subsystems do not match'

        if (code == DIGEST):
            event = DigestEvent(context, event_id, date, userInfo,
                                instanceUserInfo, siteInfo, groupInfo)
        elif (code == DIGEST_COMMAND):
            event = DigestCommand(context, event_id, date, instanceUserInfo,
                                  groupInfo, siteInfo, instanceDatum)
        elif (code == EMAIL):
            event = EmailEvent(context, event_id, date, userInfo,
                               instanceUserInfo, siteInfo, groupInfo)
        elif (code == EMAIL_COMMAND):
            event = EmailCommand(context, event_id, date, instanceUserInfo,
                                 groupInfo, siteInfo, instanceDatum)
        elif (code == WEB_ONLY):
            event = WebOnlyEvent(context, event_id, date, userInfo,
                                 instanceUserInfo, siteInfo, groupInfo)
        elif (code == ADDRESS_DEFAULT):
            event = DefaultAddressesEvent(context, event_id, date, userInfo,
                                          instanceUserInfo, siteInfo,
                                          groupInfo)
        elif (code == ADDRESS_SPECIFIC):
            event = SpecificAddressesEvent(
                context, event_id, date,  userInfo, instanceUserInfo,
                siteInfo, groupInfo, instanceDatum)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date,
                                    instanceUserInfo, instanceUserInfo,
                                    siteInfo, groupInfo, instanceDatum,
                                    supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


@implementer(IAuditEvent)
class DigestEvent(BasicAuditEvent):
    ''' An audit-trail event representing a user switching to digest-mode'''

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
                 siteInfo, groupInfo):
        """Create a leave event"""
        super(DigestEvent, self).__init__(context, id, DIGEST, d, userInfo,
                                          instanceUserInfo, siteInfo,
                                          groupInfo, None, None, SUBSYSTEM)

    @property
    def adminChanged(self):
        return self.instanceUserInfo.id != self.userInfo.id

    def __unicode__(self):
        if self.adminChanged:
            r = '{0} ({1}) has switched to digest-mode for {2} ({3}) on '\
                '({4} {5})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id)
        else:
            r = '{0} ({1}) has switched {2} ({3}) to digest-mode for '\
                '({4} {5}) on ({6} {7})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.instanceUserInfo.name,
                              self.instanceUserInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-email-settings-%s'\
                   % self.code
        r = '<span class="{0}">Switched to digest mode in {1}'
        retval = r.format(cssClass, groupInfo_to_anchor(self.groupInfo))
        if self.adminChanged:
            uu = userInfo_to_anchor(self.userInfo)
            retval = '{0} by {1}'.format(retval, uu)
        d = munge_date(self.context, self.date)
        retval = '{0}</span> ({1})'.format(retval, d)
        return retval


@implementer(IAuditEvent)
class DigestCommand(BasicAuditEvent):
    'The audit-event for an digest-command comming in.'

    def __init__(self, context, eventId, d, instanceUserInfo, groupInfo,
                 siteInfo, email):
        super(DigestCommand, self).__init__(
            context, eventId, DIGEST_COMMAND, d, instanceUserInfo,
            instanceUserInfo, siteInfo, groupInfo, email, None, SUBSYSTEM)

    def __unicode__(self):
        r = 'Email-command to switch to digest-mode for {0} ({1}) on '\
            '{2} ({3}) recieved for {4} ({5}) <{6}>.'
        retval = r.format(
            self.groupInfo.name, self.groupInfo.id,
            self.siteInfo.name, self.siteInfo.id,
            self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.instanceDatum)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-email-settings-%s'\
                   % self.code
        r = '<span class="{0}">Sent an email in to switch to digest mode '\
            'for {1}</span> ({2})'
        retval = r.format(cssClass, groupInfo_to_anchor(self.groupInfo),
                          munge_date(self.context, self.date))
        return retval


# One email per post


@implementer(IAuditEvent)
class EmailEvent(BasicAuditEvent):
    ''' An audit-trail event representing a user switching to one email
per post mode.'''

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
                 siteInfo, groupInfo):
        """Create an email event"""
        super(EmailEvent, self).__init__(context, id, EMAIL, d, userInfo,
                                         instanceUserInfo, siteInfo,
                                         groupInfo, None, None, SUBSYSTEM)

    @property
    def adminChanged(self):
        return self.instanceUserInfo.id != self.userInfo.id

    def __unicode__(self):
        if self.adminChanged:
            r = '{0} ({1}) has switched to one-email-per-post mode for '\
                '{2} ({3}) on ({4} {5})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id)
        else:
            r = '{0} ({1}) has switched {2} ({3}) to one-email-per-post '\
                'mode for ({4} {5}) on ({6} {7})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.instanceUserInfo.name,
                              self.instanceUserInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-email-settings-%s'\
                   % self.code
        r = '<span class="{0}">Switched to one-email-per-post mode in {1}'
        retval = r.format(cssClass, groupInfo_to_anchor(self.groupInfo))
        if self.adminChanged:
            uu = userInfo_to_anchor(self.userInfo)
            retval = '{0} by {1}'.format(retval, uu)
        d = munge_date(self.context, self.date)
        retval = '{0}</span> ({1})'.format(retval, d)
        return retval


@implementer(IAuditEvent)
class EmailCommand(BasicAuditEvent):
    'The audit-event for an one-email-per-post-command comming in.'

    def __init__(self, context, eventId, d, instanceUserInfo, groupInfo,
                 siteInfo, email):
        super(EmailCommand, self).__init__(
            context, eventId, EMAIL_COMMAND, d, instanceUserInfo,
            instanceUserInfo, siteInfo, groupInfo, email, None, SUBSYSTEM)

    def __unicode__(self):
        r = 'Email-command to switch off digest mode for {0} '\
            '({1}) on {2} ({3}) recieved for {4} ({5}) <{6}>.'
        retval = r.format(
            self.groupInfo.name, self.groupInfo.id,
            self.siteInfo.name, self.siteInfo.id,
            self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.instanceDatum)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-email-settings-%s'\
                   % self.code
        r = '<span class="{0}">Sent an email in to switch off digest mode '\
            'mode for {1}</span> ({2})'
        retval = r.format(cssClass, groupInfo_to_anchor(self.groupInfo),
                          munge_date(self.context, self.date))
        return retval


# Web only


@implementer(IAuditEvent)
class WebOnlyEvent(BasicAuditEvent):
    'An audit-trail event representing a user switching to Web only mode.'

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
                 siteInfo, groupInfo):
        """Create an email event"""
        super(WebOnlyEvent, self).__init__(context, id, WEB_ONLY, d,
                                           userInfo, instanceUserInfo,
                                           siteInfo, groupInfo, None, None,
                                           SUBSYSTEM)

    @property
    def adminChanged(self):
        return self.instanceUserInfo.id != self.userInfo.id

    def __unicode__(self):
        if self.adminChanged:
            r = '{0} ({1}) has switched to Web-only mode for '\
                '{2} ({3}) on ({4} {5})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id)
        else:
            r = '{0} ({1}) has switched {2} ({3}) to web-only'\
                'mode for ({4} {5}) on ({6} {7})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.instanceUserInfo.name,
                              self.instanceUserInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-email-settings-%s'\
                   % self.code
        r = '<span class="{0}">Switched to web-only mode in {1}'
        retval = r.format(cssClass, groupInfo_to_anchor(self.groupInfo))
        if self.adminChanged:
            uu = userInfo_to_anchor(self.userInfo)
            retval = '{0} by {1}'.format(retval, uu)
        d = munge_date(self.context, self.date)
        retval = '{0}</span> ({1})'.format(retval, d)
        return retval


# Addresses
@implementer(IAuditEvent)
class DefaultAddressesEvent(BasicAuditEvent):
    '''An audit-trail event representing a user switching to the default
email addresses.'''

    def __init__(self, context, eventId, d, userInfo, instanceUserInfo,
                 siteInfo, groupInfo):
        """Create an email event"""
        super(DefaultAddressesEvent, self).__init__(
            context, eventId,  ADDRESS_DEFAULT, d, userInfo,
            instanceUserInfo, siteInfo, groupInfo, None, None,
            SUBSYSTEM)

    @property
    def adminChanged(self):
        return self.instanceUserInfo.id != self.userInfo.id

    def __unicode__(self):
        if self.adminChanged:
            r = '{0} ({1}) has switched to the using the default '\
                'addresses for {2} ({3}) on ({4} {5})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id)
        else:
            r = '{0} ({1}) has switched {2} ({3}) to use the default'\
                'addresses for ({4} {5}) on ({6} {7})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.instanceUserInfo.name,
                              self.instanceUserInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-email-settings-%s'\
                   % self.code
        r = '<span class="{0}">Switched to use the default addresses in '\
            '{1}'
        retval = r.format(cssClass, groupInfo_to_anchor(self.groupInfo))
        if self.adminChanged:
            uu = userInfo_to_anchor(self.userInfo)
            retval = '{0} by {1}'.format(retval, uu)
        d = munge_date(self.context, self.date)
        retval = '{0}</span> ({1})'.format(retval, d)
        return retval


@implementer(IAuditEvent)
class SpecificAddressesEvent(BasicAuditEvent):
    '''An audit-trail event representing a user switching to specific email
addresses.'''

    def __init__(self, context, eventId, d, userInfo, instanceUserInfo,
                 siteInfo, groupInfo, addresses):
        """Create an email event"""
        super(SpecificAddressesEvent, self).__init__(
            context, eventId,  ADDRESS_SPECIFIC, d, userInfo,
            instanceUserInfo, siteInfo, groupInfo, addresses, None,
            SUBSYSTEM)

    @property
    def adminChanged(self):
        return self.instanceUserInfo.id != self.userInfo.id

    def __unicode__(self):
        addrs = self.instanceDatum.split()
        addrStr = comma_comma_and(addrs)
        if self.adminChanged:
            r = '{0} ({1}) has switched to the specific email addresses '\
                '{6} for {2} ({3}) on ({4} {5})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id,
                              addrStr)
        else:
            r = '{0} ({1}) has switched {2} ({3}) to use the specific'\
                'addresses {8} for ({4} {5}) on ({6} {7})'
            retval = r.format(self.userInfo.name, self.userInfo.id,
                              self.instanceUserInfo.name,
                              self.instanceUserInfo.id,
                              self.groupInfo.name, self.groupInfo.id,
                              self.siteInfo.name, self.siteInfo.id,
                              addrStr)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-email-settings-%s'\
                   % self.code
        addrs = ['<code class="email">{0}</code>'.format(a) for a in
                 self.instanceDatum.split()]
        addrStr = comma_comma_and(addrs)
        r = '<span class="{0}">Switched to use the email addresses {1} in '\
            '{2}'
        retval = r.format(cssClass, addrStr,
                          groupInfo_to_anchor(self.groupInfo))
        if self.adminChanged:
            uu = userInfo_to_anchor(self.userInfo)
            retval = '{0} by {1}'.format(retval, uu)
        d = munge_date(self.context, self.date)
        retval = '{0}</span> ({1})'.format(retval, d)
        return retval


# Auditor


class SettingsAuditor(object):
    """An Auditor for changing the settings"""
    def __init__(self, context, userInfo, instanceUserInfo, groupInfo):
        """Create a leaving auditor."""
        self.context = context
        self.instanceUserInfo = instanceUserInfo
        self.userInfo = userInfo
        self.__groupInfo = groupInfo

    @Lazy
    def siteInfo(self):
        retval = createObject('groupserver.SiteInfo', self.context)
        return retval

    @Lazy
    def groupInfo(self):
        retval = self.__groupInfo if self.__groupInfo is not None else \
            createObject('groupserver.GroupInfo', self.context)
        return retval

    @Lazy
    def factory(self):
        retval = GroupEmailSettingsAuditEventFactory()
        return retval

    @Lazy
    def queries(self):
        retval = AuditQuery()
        return retval

    def info(self, code, instanceDatum='', supplementaryDatum=''):
        """Log an info event to the audit trail.
            * Creates an ID for the new event,
            * Writes the instantiated event to the audit-table, and
            * Writes the event to the standard Python log.
        """
        d = datetime.now(UTC)
        eventId = event_id_from_data(
            self.userInfo, self.instanceUserInfo, self.siteInfo, code,
            instanceDatum, supplementaryDatum)

        e = self.factory(self.context, eventId, code, d, self.userInfo,
                         self.instanceUserInfo, self.siteInfo,
                         self.groupInfo, instanceDatum, supplementaryDatum,
                         SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
        return e
