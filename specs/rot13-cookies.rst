=======================================
Website with ROT-13 "encrypted" cookies
=======================================

As a simple starter exercise, we'll attack a website that "encrypts"
its cookies using ROT13.

Cookie structure
================

The plaintext cookies are key-value pairs. Keys are separated from
values with ``=``, pairs are separated from each other with ``&``. For
example::

    name=johnny&age=10&pet=rufus

The goal of this exercise is to get admin access to the website. The
website gives admin access to anyone who has an ``admin=1`` pair.

ROT13
=====

ROT13 is a very simple encoding scheme that replaces every letter with
one 13 letters further in the alphabet. Since the alphabet has 26
letters, this has the interesting property that encrypting and
decrypting is exactly the same operation. You can use this table to
translate:

    abcdefghijklmnopqrstuvwxyz
    nopqrstuvwxyzabcdefghijklm

All other bytes are unchanged.

Since it doesn't involve any secret data, it doesn't really count as a
form of encryption. People use it, for example, for giving out
spoilers in a newsgroup for nethack, a video game. That way, people
who want to read the spoiler have to go out of their way to read it;

Attack walkthrough
==================

Create a proxy connection to ``rot13-cookies-site`` (don't include the
quotes). Connect to the port it tells you to. It's a web site, so a
web browser is probably easiest. You'll be able to register. Once you
do that, you get a cookie. Edit the cookie so it has the admin key
pair in there, and see if it worked.
