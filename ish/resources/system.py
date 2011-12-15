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
	creation_query = """SELECT api.create_system('{name}', '{owner}', '{sys_type}', '{os_name}', '{comment}');""" # Query to create an object

	def __init__(self, name, owner, sys_type=None, os=None, comment=None):
		if name: self.system_name = name
		if owner: self.owner = owner
		if sys_type: self.sys_type = sys_type
		if os: self.os_name = os
		if comment: self.comment = comment
		else: comment = 'NULL'

	def create(self):
		query = self.creation_query.format(name=self.system_name, owner=self.owner, sys_type=self.sys_type, os_name=self.os_name, comment=self.comment)
		ImpulseObject.create(self, query)
		return True


class Interface(ImpulseObject):
	system_name = None
	mac = None
	comment = None
	removal_parameter = "mac" # What parameter does the deletion query require?
	removal_query = """SELECT api.remove_interface('%s');""" # Query that removes the object
	creation_query = """SELECT api.create_interface('{name}', '{mac}', '{comment}');""" # Query to create an object

	def __init__(self, name, mac, comment=None):
		self.system_name = name
		self.mac = mac
		if comment: self.comment = comment
		else: self.comment = 'NULL'

	def create(self):
		query = self.creation_query.format(name=self.system_name, mac=self.mac, comment=self.comment)
		ImpulseObject.create(self, query)

