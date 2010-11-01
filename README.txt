.. sectnum::

============
Introduction
============

This component contains the code and form to allow people to change
their group specific email settings.

===================
Email Settings Page
===================

The ``email_settings.html`` page, in a group, is used by people who are either
**logged** **in**, and a group member, or a site admin, to change the email
settings related to a group membership. If no ``userId`` parameter is given
to the form, the page will edit the current user's settings. Otherwise, the
settings of the specified user may be modified.
