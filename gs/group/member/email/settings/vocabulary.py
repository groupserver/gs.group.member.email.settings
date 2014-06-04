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
        self.defaultAddress = ''
        if defaultAddresses:
            self.defaultAddress = defaultAddresses[0]

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        retval = [SimpleTerm('default', 'default', 'Default (%s)' %
                                self.defaultAddress),
                   SimpleTerm('specific', 'specific',
                               'Specific Address or Addresses'),
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
                                'Default (%s)' % self.defaultAddress)
        elif token == 'specific':
            retval = SimpleTerm('specific', 'specific',
                                    'Specific Address or Addresses')
        if retval:
            return retval
        raise LookupError(token)
