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
from zope.interface import Interface
from zope.schema import TextLine, Choice, List
from Products.GSProfile.interfaces import deliveryVocab


class IGSGroupEmailUserId(Interface):
    userId = TextLine(
        title="User Id",
        description="The ID of the user being edited",
        required=True)


class IGSGroupEmailDeliverySettings(Interface):
    delivery = Choice(
        title='Message Delivery',
        description='Your message delivery settings.',
        vocabulary=deliveryVocab)


class IGSGroupEmailDestinationSettings(Interface):
    default_or_specific = Choice(
        title="Message Destination",
        description='Should the message go to your '
                    'default email address, or a specific one?',
        vocabulary="DefaultOrSpecificEmailVocab",
        required=True)

    destination = List(
        title='Message Destination',
        description='Your message delivery settings.',
        value_type=Choice(title='Email',
                          vocabulary="EmailAddressesForUser"),
        unique=True,
        required=False)


class IGSGroupEmailSettings(IGSGroupEmailUserId,
                            IGSGroupEmailDeliverySettings,
                            IGSGroupEmailDestinationSettings):
    pass
