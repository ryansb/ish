#!/usr/bin/env python
# -*- coding; utf-8 -*-
# Author: Ryan Brown
# Description: 
#
# Copyright (c) 2011 Ryan Brown ryansb@csh.rit.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions;

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from ish.resources import ImpulseObject

class System(ImpulseObject):
	system_name = None # Name of the system
	owner = None # Owning user (NULL for current authenticated user)
	sys_type = None # Server, Desktop, Laptop, etc
	os_name = None # Primary operating system
	comment = None # Comment on the system (or NULL for no comment)
	removal_parameter = "system_name" # What parameter does the deletion query require?
	removal_query = """SELECT api.remove_system('%s');""" # Query that removes the object
	creation_query = """SELECT api.create_system('{name}', '{owner}', '{sys_type}', '{os_name}', '{comment}')""" # Query to create an object

	def __init__(self, name=None, owner=None, sys_type=None, os=None, comment=None):
		self.system_name = name
		self.owner = owner
		self.sys_type = sys_type
		self.os_name = os
		self.comment = comment
		if name and owner and sys_type and os: self.create()

	def create(self):
		if not (self.system_name and self.owner and self.sys_type and self.os_name):
			raise Exception("Missing Parameter.\nSystem name: %s\nOwner: %s\nSystem type: %s\nOS: %s\n"
					% (self.system_name, self.owner, self.sys_type, self.os_name))
		if not self.comment: self.comment = "NULL"
		query = self.creation_query.format(name=self.system_name,
				owner=self.owner, sys_type=self.sys_type, os_name=self.os_name,
				comment=self.comment)
		return ImpulseObject.create(query)


class Interface(ImpulseObject):
	system_name = None # Name of the system
	mac = None # Owning user (NULL for current authenticated user)
	comment = None # Comment on the system (or NULL for no comment)
	removal_parameter = "mac" # What parameter does the deletion query require?
	removal_query = """SELECT api.remove_interface('%s');""" # Query that removes the object
	creation_query = """SELECT api.create_interface('{name}', '{mac}', {comment}')""" # Query to create an object

	def __init__(self, name, mac, comment=None):
		self.system_name = name
		self.mac = mac
		self.comment = comment
