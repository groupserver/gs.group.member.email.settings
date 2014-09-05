==================================
``gs.group.member.email.settings``
==================================

Introduction
============

This component contains the code and form to allow people to
change their group-specific email settings_, using the `email
settings page`_.

Settings
========

Conceptually, email settings can be tricky to understand, because
there are two sets of interlinked settings, for delivery_ and
email_.

Delivery
--------

The delivery settings determine the *quantity* of email the group
member receives. There are three possible delivery settings:

  1.  One email per post (default). An email message is sent when
      anyone posts to the group.

  2.  Daily digest of topics. At most one email is sent per day,
      summarising the activity in the group [#digest]_

  3.  No email (Web only).

Email
-----

The email settings determine *where* the messages are sent. If
one of the first two delivery_ settings are selected then email
is sent to one *or more* of the email addresses controlled by the
group member. However the messages can be sent to the **default**
list of addresses [#settings]_, or a **specific** address (or set
of addresses).
  
Email Settings Page
===================

The ``email_settings.html`` page, in the group context group, is
used by people who are either

* **Logged in**, and a group member, or 
* A **site** administrator.

It allows either to change the email settings related to a group
membership. If no ``userId`` parameter is given to the form, the
page will edit the current user's settings. Otherwise, the
settings of the specified user will be modified.

The JavaScript resource
``gs-group-member-email-settings-20140604.js`` is used to provide
the interlock between the delivery settings, and the email
settings.

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.group.member.email.settings
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Richard Waid: http://groupserver.org/p/richard
.. _Creative Commons Attribution-Share Alike 3.0 New Zealand License:
   http://creativecommons.org/licenses/by-sa/3.0/nz/
..  [#digest] See ``gs.group.messages.topicsdigest`` for details
              <https://source.iopen.net/groupserver/gs.group.messages.topicsdigest/>

.. [#settings] See ``gs.profile.email.settings`` for details
               <https://source.iopen.net/groupserver/gs.profile.email.settings/>

