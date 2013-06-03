# -*- coding: utf-8 -*-
from zope.component import createObject
from zope.interface import implements
from zope.interface.common.mapping import IEnumerableMapping
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm
from Products.CustomUserFolder.interfaces import IGSUserInfo
from gs.profile.email.base.emailuser import EmailUser


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

        emailUser = EmailUser(self.userInfo.user, self.userInfo)
        defaultAddresses = emailUser.get_delivery_addresses()
        self.defaultAddress = u''
        if defaultAddresses:
            self.defaultAddress = defaultAddresses[0]

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        retval = [SimpleTerm('default', 'default', u'Default (%s)' %
                                self.defaultAddress),
                   SimpleTerm('specific', 'specific',
                               u'Specific Address or Addresses'),
                 ]
        return iter(retval)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return 2

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = False
        if value in ('specific', 'default'):
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
            retval = SimpleTerm('default', 'default',
                                u'Default (%s)' % self.defaultAddress)
        elif token == 'specific':
            retval = SimpleTerm('specific', 'specific',
                                    u'Specific Address or Addresses')
        if retval:
            return retval
        raise LookupError(token)
