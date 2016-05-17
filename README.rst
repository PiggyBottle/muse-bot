********
muse-bot
********

Hexchat IRC bot for Muse-chan

Dependencies:
=============
`Oauth2`_

How to install:
---------------

1. Download the tar.gz and open with WinRAR. Extract folder out.
2. Go to Windows Explorer and right-click 'This Computer', and click 'Properties'.
3. Click 'Advanced System Settings' and then 'Environment Variables'. Edit the 'Path' variable and append ';c:\Python34' to it.
4. Open CMD in Administrator Mode and cd to Pastebin folder. Type 'python setup.py install'.

Installing Muse
===============

To install ``muse-bot``, you need to clone this repo. For your convenience, the command is

::

    git clone https://github.com/SoraSkyy/muse-bot


Configuration:
--------------

In the file ``setup.cfg``, the channels the bot enters (+ optional passwords), the name of the bot (again, + optional passwords), email address + password, and the nickname of the bot's "master" are configured.

Running Muse
============

Currently, the bot is run through the command ``sudo python3 bot.py``.

.. _Oauth2: https://github.com/joestump/python-oauth2
