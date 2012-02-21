====
Impulse Shell (ish)
====

=======
About
=======
Impulse Shell is the command-line interface for Impulse_ and is intended to
allow easy programmatic actions on systems in Impulse.

.. _Impulse: https://github.com/cohoe/impulse

The shell portion of ish is a modified Python shell, so it's possible to use
normal Python programming constructs like for, if, and list interpretations.

This README is written in ReST_.

.. _ReST: http://docutils.sourceforge.net/docs/user/rst/quickref.html

=======
Commands
=======

From inside of ish (start with the command 'ish')

# You can get a system by its name and it will only return a single system

>>> mysystem = System.find('thename')

# Or you can search by any parameter of an object, not just its name

# Some parameters are owner, last_modifier, type, and os_name

>>> all_my_systems = System.search(owner='myname')

>>> all_fedora_systems = System.search(os_name='Fedora')

>>> print all_my_systems

[system1, system2, system3]

>>> mysys = all_my_systems[0]

>>> print mysys.name

system1

>>> mysys.os_name

Gentoo

>>> mysys.os_name = "Fedora"

>>> mysys.put()


>>> mysys.os_name

Fedora

========
impulse-query
========
The impulse-query command is a quick way to perform a query

impulse-query -t <object type> [-p <param> <param value>]

If no params are given, it will list every object of that type. This may take some time.
