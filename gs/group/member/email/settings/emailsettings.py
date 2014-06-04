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
from zope.component import createObject
from zope.formlib import form
from zope.interface import alsoProvides
from zope.security import checkPermission
from zope.security.interfaces import Unauthorized
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.content.form import radio_widget, multi_check_box_widget
from gs.group.base import GroupForm
from gs.group.member.base.utils import user_member_of_group
from gs.profile.email.base.emailuser import EmailUser
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
        userInfo = self.userInfo

        groupId = self.groupInfo.id
        # further sanity/security check
        if not user_member_of_group(userInfo, self.context):
            raise Unauthorized("User %s was not a member of the group %s" %
                                (userInfo.id, groupId))
        u = userInfo.user
        specificEmailAddresses = u.get_specificEmailAddressesByKey(groupId)
        deliverySettings = userInfo.user.get_deliverySettingsByKey(groupId)
        delivery = 'email'
        default_or_specific = 'default'
        if deliverySettings == 0:
            delivery = 'web'
        elif deliverySettings == 3:
            delivery = 'digest'
        elif deliverySettings == 2:
            default_or_specific = 'specific'

        default_data = {'default_or_specific': default_or_specific,
                        'destination': specificEmailAddresses,
                        'delivery': delivery,
                        'userId': userInfo.id}

        alsoProvides(userInfo, IGSGroupEmailSettings)
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, userInfo, self.request,
            data=default_data,
            ignore_request=False)

    @property
    def is_editing_self(self):
        """ Check to see if we are editing ourselves, or another user.

        """
        me = self.loggedInUser
        userId = self.request.get('userId') or self.request.get('form.userId')

        editing_self = True
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

    @form.action(label='Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        deliveryMethod = data['delivery']
        defaultOrSpecific = data['default_or_specific']
        emailAddresses = data['destination']

        assert deliveryMethod in ('email', 'digest', 'web'), \
            "Unexpected delivery option %s" % deliveryMethod
        if deliveryMethod != 'web':
            assert defaultOrSpecific in ('default', 'specific'), \
                "Unexpected defaultOrSpecific %s" % defaultOrSpecific
            assert isinstance(emailAddresses, list), \
                "destination addresses %s are not in a list" % emailAddresses

        groupId = self.groupInfo.id
        user = self.userInfo.user
        if self.is_editing_self:
            name = '<a href="%s">You</a>' % self.userInfo.url
        else:
            name = '<a href="%s">%s</a>' % (self.userInfo.url,
                                             self.userInfo.name)

        groupName = '<a href="%s">%s</a>' % (self.groupInfo.relativeURL,
                                              self.groupInfo.name)

        m = ""
        # enable delivery to clear the delivery settings
        user.set_enableDeliveryByKey(groupId)
        if deliveryMethod == 'email':
            m += '<strong>%s</strong> will receive an email message '\
                'every time someone posts to %s.' % (name, groupName)
        elif deliveryMethod == 'digest':
            user.set_enableDigestByKey(groupId)
            m += '<strong>%s</strong> will receive a daily digest of '\
                'topics posted to %s.' % (name, groupName)
        elif deliveryMethod == 'web':
            user.set_disableDeliveryByKey(groupId)
            m += '<strong>%s</strong> will not receive any email from ' \
                 '%s.' % (name, groupName)
        m += ' '
        if deliveryMethod != 'web':
            # reset the specific addresses
            specificAddresses = user.get_specificEmailAddressesByKey(groupId)
            for address in specificAddresses:
                user.remove_deliveryEmailAddressByKey(groupId, address)

            if defaultOrSpecific == 'specific' and emailAddresses:
                m += 'Email will be delivered to:\n<ul>'
                for address in emailAddresses:
                    user.add_deliveryEmailAddressByKey(groupId, address)
                    m += '<li><code class="email">%s</code></li>' % address
                m += '</ul>\n'
            else:
                emailUser = EmailUser(self.context, self.userInfo)
                address = emailUser.get_delivery_addresses()[0]
                m += 'Email will be delivered to the default address, which '\
                    'is: <code class="email">%s</code>' % address
        self.status = m

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = '<p>There is an error:</p>'
        else:
            self.status = '<p>There are errors:</p>'
