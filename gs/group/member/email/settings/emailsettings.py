# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2010, 2011, 2012, 2013, 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, getMultiAdapter
from zope.formlib import form
from zope.interface import alsoProvides
from zope.security import checkPermission
from zope.security.interfaces import Unauthorized
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.content.form import radio_widget, multi_check_box_widget
from gs.core import comma_comma_and
from gs.group.base import GroupForm
from gs.group.member.base.utils import user_member_of_group
from gs.group.member.email.base.interfaces import IGroupEmailUser
from gs.group.member.email.base import GroupEmailSetting
from .interfaces import IGSGroupEmailSettings


class GroupEmailSettingsForm(GroupForm):
    label = 'Email Settings'
    pageTemplateFileName = 'browser/templates/groupemailsettings.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSGroupEmailSettings, render_context=True)

    def __init__(self, group, request):
        super(GroupEmailSettingsForm, self).__init__(group, request)
        self.form_fields['delivery'].custom_widget = radio_widget
        self.form_fields['default_or_specific'].custom_widget = radio_widget
        self.form_fields['destination'].custom_widget = multi_check_box_widget

    def setUpWidgets(self, ignore_request=True):
        groupId = self.groupInfo.id
        # further sanity/security check
        if not user_member_of_group(self.userInfo, self.context):
            m = "User {0} was not a member of the group {1}"
            msg = m.format(self.userInfo.id, groupId)
            raise Unauthorized(msg)
        specificEmailAddresses = \
                            self.groupEmailUser.get_specific_email_addresses()
        deliverySetting = self.groupEmailUser.get_delivery_setting()
        delivery = 'email'
        default_or_specific = 'default'
        if deliverySetting == GroupEmailSetting.webonly:
            delivery = 'web'
        elif deliverySetting == GroupEmailSetting.digest:
            delivery = 'digest'
        elif deliverySetting == GroupEmailSetting.specific:
            default_or_specific = 'specific'

        default_data = {'default_or_specific': default_or_specific,
                        'destination': specificEmailAddresses,
                        'delivery': delivery,
                        'userId': self.userInfo.id}

        alsoProvides(self.userInfo, IGSGroupEmailSettings)
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.userInfo, self.request,
            data=default_data,
            ignore_request=False)

    @property
    def is_editing_self(self):
        """ Check to see if we are editing ourselves, or another user."""
        me = self.loggedInUser
        userId = self.request.get('userId') or self.request.get('form.userId')

        editing_self = True
        # editing_self = (userId is not None) and (me.userId == userId)
        if userId:
            if me.id != userId:
                editing_self = False

        return editing_self

    @Lazy
    def userInfo(self):
        userId = self.request.get('userId') or self.request.get('form.userId')
        if userId:
            user = getattr(self.context.contacts, userId)
            if not checkPermission("zope2.ManageProperties", user):
                m = "Not authorized to manage the settings of user {0}."
                msg = m.format(userId)
                raise Unauthorized(msg)
            retval = createObject('groupserver.UserFromId', self.context,
                                    userId)
        else:
            retval = self.loggedInUser
        return retval

    @Lazy
    def groupEmailUser(self):
        retval = getMultiAdapter((self.userInfo, self.groupInfo),
                                    IGroupEmailUser)
        return retval

    @form.action(label='Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        deliveryMethod = data['delivery']
        defaultOrSpecific = data['default_or_specific']
        emailAddresses = data['destination']

        assert deliveryMethod in ('email', 'digest', 'web'), \
            "Unexpected delivery option %s" % deliveryMethod
        if deliveryMethod != 'web':
            if defaultOrSpecific not in ('default', 'specific'):
                errMsg = "Unexpected defaultOrSpecific %s" % defaultOrSpecific
                raise ValueError(errMsg)
            if not(isinstance(emailAddresses, list)):
                errM = "destination addresses {0} are not in a list"
                errMsg = errM.format(emailAddresses)
                raise TypeError(errMsg)

        if self.is_editing_self:
            name = '<a href="%s">You</a>' % self.userInfo.url
        else:
            name = '<a href="%s">%s</a>' % (self.userInfo.url,
                                             self.userInfo.name)
        groupName = '<a href="%s">%s</a>' % (self.groupInfo.relativeURL,
                                              self.groupInfo.name)
        m = ""
        self.groupEmailUser.set_default_delivery()
        if deliveryMethod == 'email':
            m += '<strong>%s</strong> will receive an email message '\
                'every time someone posts to %s.' % (name, groupName)
        elif deliveryMethod == 'digest':
            self.groupEmailUser.set_digest()
            m += '<strong>%s</strong> will receive a daily digest of '\
                'topics posted to %s.' % (name, groupName)
        elif deliveryMethod == 'web':
            self.groupEmailUser.set_webonly()
            m += '<strong>%s</strong> will not receive any email from ' \
                 '%s.' % (name, groupName)
        m += ' '
        if deliveryMethod != 'web':
            # reset the specific addresses
            if defaultOrSpecific == 'specific' and emailAddresses:
                m += 'Email will be delivered to:\n<ul>'
                for address in emailAddresses:
                    self.groupEmailUser.add_specific_address(address)
                    m += '<li><code class="email">%s</code></li>' % address
                m += '</ul>\n'
            else:
                addrs = ['<code class="email">{0}</code>'.format(a) for a in
                        self.groupEmailUser.get_preferred_email_addresses()]
                plural = 'address' if len(addrs) == 1 else 'addresses'
                m += 'Email will be delivered to the default {0}, which '\
                    'is: {1}'.format(plural, comma_comma_and(addrs))
        self.status = m

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = '<p>There is an error:</p>'
        else:
            self.status = '<p>There are errors:</p>'
