# coding=utf-8
from zope.interface import Interface
from zope.schema import *
from Products.GSProfile.interfaces import deliveryVocab

class IGSGroupEmailDeliverySettings(Interface):
    delivery = Choice(title=u'Message Delivery',
      description=u'Your message delivery settings.',
      vocabulary=deliveryVocab)

class IGSGroupEmailDestinationSettings(Interface):
    default_or_specific = Choice(title=u"Message Destination",
                                 description=u"Should the message go to your default email address, or a specific one?",
                                 vocabulary="DefaultOrSpecificEmailVocab",
                                 required=True)
    
    destination = List(title=u'Message Destination',
                       description=u'Your message delivery settings.',
                       value_type=Choice(title=u'Email',
                                         vocabulary="EmailAddressesForUser"),
                       unique=True,
                       required=False)

class IGSGroupEmailSettings(IGSGroupEmailDeliverySettings, IGSGroupEmailDestinationSettings):
    pass
   
    


