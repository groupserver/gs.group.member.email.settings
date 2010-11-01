# coding=utf-8
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm
from zope.interface import implements, providedBy, alsoProvides
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabulary, \
  IVocabularyTokenized, ITitledTokenizedTerm
from zope.security import checkPermission, canAccess
from zope.interface.common.mapping import IEnumerableMapping
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.content.form.radio import radio_widget
from Products.GSProfile.edit_profile import multi_check_box_widget
from Products.GSGroupMember.groupmembership import user_member_of_group
from interfaces import IGSGroupEmailSettings
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.CustomUserFolder.interfaces import ICustomUser
from Products.GSGroupMember.groupmembership import user_member_of_group
from zope.security.interfaces import Unauthorized

class GroupEmailSettingsForm(PageForm):
    label = u'GroupEmailSettings'
    pageTemplateFileName = 'browser/templates/groupemailsettings.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSGroupEmailSettings, render_context=True)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.context = context
        self.request = request
        self.__siteInfo = self.__groupInfo = self.__userInfo = None
        self.__mailingListInfo = None
        self.form_fields['delivery'].custom_widget = radio_widget
        self.form_fields['default_or_specific'].custom_widget = radio_widget
        self.form_fields['destination'].custom_widget = multi_check_box_widget
        
    def setUpWidgets(self, ignore_request=True):
        userId = self.request.get('userId')
        if self.request.get('userId'):
            user = getattr(self.ctx.contacts, userId)
            if not checkPermission("zope2.ManageProperties", user):
                raise Unauthorized("Not authorized to manage the settings of user %s." % (userId))
            userInfo = IGSUserInfo(user)
        else:
            userInfo = self.userInfo

        groupId = self.ctx.getId()
        # further sanity/security check
        if not user_member_of_group(userInfo, self.ctx):
             raise Unauthorized("User %s was not a member of the group %s" % 
                                (userInfo.id, groupId))
        
        specificEmailAddresses = userInfo.user.get_specificEmailAddressesByKey(groupId)
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
                        'delivery': delivery}
        
        alsoProvides(userInfo, IGSGroupEmailSettings)
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, userInfo, self.request,
            data=default_data,
            ignore_request=False)
    
    def is_editing_self(self):
        """ Check to see if we are editing ourselves, or another user.
        
        """
        userId = self.request.get('userId')
        editing_self = True
        if userId:
            if self.userInfo.id != userId:
                editing_self = False
        
        return editing_self
    
    @property 
    def ctx(self):
        return get_the_actual_instance_from_zope(self.context)        
        
    @property
    def siteInfo(self):
        if self.__siteInfo == None:
            self.__siteInfo = createObject('groupserver.SiteInfo', 
                                self.ctx)
        assert self.__siteInfo
        return self.__siteInfo

    @property
    def groupInfo(self):
        if self.__groupInfo == None:
            self.__groupInfo = createObject('groupserver.GroupInfo', 
                                self.ctx)
        assert self.__groupInfo
        return self.__groupInfo

    @property
    def userInfo(self):
        if self.__userInfo == None:
            self.__userInfo = createObject('groupserver.LoggedInUser',
                                  self.context)
        return self.__userInfo
        
    @form.action(label=u'Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        print data
        deliveryMethod = data['delivery']
        defaultOrSpecific = data['default_or_specific']
        emailAddresses = data['destination']
        
        assert deliveryMethod in ('email','digest','web'), "Unexpected delivery option %s" % deliveryMethod
        if deliveryMethod != 'web':
            assert defaultOrSpecific in ('default','specific'), "Unexpected defaultOrSpecific %s" % defaultOrSpecific
            assert isinstance(emailAddresses, list), "destination addresses %s are not in a list" % emailAddresses
        
        groupId = self.groupInfo.id
        user = self.userInfo.user
        if self.is_editing_self:
            name = u'You'
        else:
            name = self.userInfo.name
        
        # enable delivery to clear the delivery settings
        user.set_enableDeliveryByKey(groupId)
        if deliveryMethod == 'email':
            m = u'%s will receive an email message every time '\
                    u'someone posts to %s.' % (name, self.groupInfo.name)   
        elif deliveryMethod == 'digest':
            user.set_enableDigestByKey(groupId)
            m = u'%s will receive a daily digest of topics.' % name
        elif deliveryMethod == 'web':
            user.set_disableDeliveryByKey(groupId)
            m = u'%s will not receive any email from this group.' % name
        
        if deliveryMethod != 'web':
            # reset the specific addresses
            specificAddresses = user.get_specificEmailAddressesByKey(groupId)
            for address in specificAddresses:
                user.remove_deliveryEmailAddressByKey(groupId, address)
                
            if defaultOrSpecific == 'specific':
                for address in emailAddresses:
                    user.add_deliveryEmailAddressByKey(groupId, address)
            
        self.status = u'You have joined <a class="group" href="%s">%s</a>. %s' %\
          (self.groupInfo.url, self.groupInfo.name, m)
        
        assert type(self.status) == unicode
        
    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

class DefaultOrSpecificEmailVocab(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context
        # the context we are passed might already be a userinfo
        if IGSUserInfo.providedBy(context):
            self.userInfo = context
        else:
            self.userInfo = createObject('groupserver.LoggedInUser', context)

        defaultAddresses = self.userInfo.user.get_defaultDeliveryEmailAddresses()
        self.defaultAddress = u''
        if defaultAddresses:
            self.defaultAddress = defaultAddresses[0]
          
    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        retval = [ SimpleTerm('default', 'default', u'Default (%s)' % self.defaultAddress),
                   SimpleTerm('specific', 'specific', u'Specific Address or Addresses'),
                 ]

        return iter(retval)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return 2

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = False
        if value in ('specific','default'):
            retval = True
        assert type(retval) == bool
        return retval

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return self.getTermByToken(value)
        
    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        retval = None
        if token == 'default':
            retval = SimpleTerm('default', 'default', u'Default (%s)' % self.defaultAddress)
        elif token == 'specific':
            retval = SimpleTerm('specific','specific',u'Specific Address or Addresses')
            
        if retval:
            return retval

        raise LookupError, token
