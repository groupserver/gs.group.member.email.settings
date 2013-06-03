# -*- coding: utf-8 -*-
from zope.cachedescriptors import Lazy
from zope.component import createObject
from zope.formlib import form
from zope.interface import alsoProvides
from zope.security import checkPermission
from zope.security.interfaces import Unauthorized
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.content.form import radio_widget
from gs.group.base import GroupForm
from gs.profile.email.base.emailuser import EmailUser
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from Products.GSProfile.edit_profile import multi_check_box_widget
from Products.GSGroupMember.groupmembership import user_member_of_group
from interfaces import IGSGroupEmailSettings


class GroupEmailSettingsForm(GroupForm):
    label = u'GroupEmailSettings'
    pageTemplateFileName = 'browser/templates/groupemailsettings.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSGroupEmailSettings, render_context=True)

    def __init__(self, context, request):
        super(GroupEmailSettingsForm, self).__init__(context, request)
        self.__userInfo = None
        self.__mailingListInfo = None
        self.form_fields['delivery'].custom_widget = radio_widget
        self.form_fields['default_or_specific'].custom_widget = radio_widget
        self.form_fields['destination'].custom_widget = multi_check_box_widget

    def setUpWidgets(self, ignore_request=True):
        userInfo = self.userInfo

        groupId = self.ctx.getId()
        # further sanity/security check
        if not user_member_of_group(userInfo, self.ctx):
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
        me = createObject('groupserver.LoggedInUser', self.context)
        userId = self.request.get('userId') or self.request.get('form.userId')

        editing_self = True
        if userId:
            if me.id != userId:
                editing_self = False

        return editing_self

    @property
    def ctx(self):
        return get_the_actual_instance_from_zope(self.context)

    @Lazy
    def userInfo(self):
        userId = self.request.get('userId') or self.request.get('form.userId')
        if userId:
            retval = createObject('groupserver.UserFromID', self.context,
                                    userId)
            if not checkPermission("zope2.ManageProperties", retval.user):
                m = "Not authorized to manage the settings of user {0}."
                msg = m.format(userId)
                raise Unauthorized(msg)
        else:
            retval = super(GroupEmailSettingsForm, self).userInfo
        return retval

    @form.action(label=u'Change', failure='handle_change_action_failure')
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
            name = u'<a href="%s">You</a>' % self.userInfo.url
        else:
            name = u'<a href="%s">%s</a>' % (self.userInfo.url,
                                             self.userInfo.name)

        groupName = u'<a href="%s">%s</a>' % (self.groupInfo.relativeURL,
                                              self.groupInfo.name)

        m = u""
        # enable delivery to clear the delivery settings
        user.set_enableDeliveryByKey(groupId)
        if deliveryMethod == 'email':
            m += u'<strong>%s</strong> will receive an email message '\
                u'every time someone posts to %s.' % (name, groupName)
        elif deliveryMethod == 'digest':
            user.set_enableDigestByKey(groupId)
            m += u'<strong>%s</strong> will receive a daily digest of '\
                u'topics posted to %s.' % (name, groupName)
        elif deliveryMethod == 'web':
            user.set_disableDeliveryByKey(groupId)
            m += u'<strong>%s</strong> will not receive any email from ' \
                 u'%s.' % (name, groupName)
        m += u' '
        if deliveryMethod != 'web':
            # reset the specific addresses
            specificAddresses = user.get_specificEmailAddressesByKey(groupId)
            for address in specificAddresses:
                user.remove_deliveryEmailAddressByKey(groupId, address)

            if defaultOrSpecific == 'specific' and emailAddresses:
                m += u'Email will be delivered to:\n<ul>'
                for address in emailAddresses:
                    user.add_deliveryEmailAddressByKey(groupId, address)
                    m += u'<li><code class="email">%s</code></li>' % address
                m += u'</ul>\n'
            else:
                emailUser = EmailUser(self.context, self.userInfo)
                address = emailUser.get_delivery_addresses()[0]
                m += u'Email will be delivered to the default address, which '\
                    u'is: <code class="email">%s</code>' % address
        self.status = m

        assert type(self.status) == unicode

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'
