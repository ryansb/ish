====
Impulse Shell (ish)
====

=======
About
=======
Impulse Shell is the command-line interface for Impulse_ and is intended to
allow easy programmatic actions on systems in Impulse.

.. _https://github.com/cohoe/impulse

The shell portion of ish is a modified Python shell, so it's possible to use
normal Python programming constructs like for, if, and list interpretations.

This README is written in ReST_.

.. _http://docutils.sourceforge.net/docs/user/rst/quickref.html

=======
Commands
=======

impulse-query -t <object type> [-p <param> <param value>]

If no params are given, it will list every object of that type. This may take some time.

impulse-quick-create <name-of-system>

========
impulse-query
========
The impulse-query command is a quick way to perform a query
