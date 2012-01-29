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
from ish.resources import ImpulseObject, ImmutabilityMeta
from ish import get_username


class System(ImpulseObject):
	__metaclass__ = ImmutabilityMeta
	pkey = "system_name"  # What parameter does the deletion query require?
	table_name = 'systems'
	schema_name = 'systems'
	required_properties = ('system_name', 'sys_type', 'os_name')
	optional_properties = ('comment', )
	removal_query = """SELECT api.remove_system('%s');"""
	# Query to remove the object
	creation_query = ("SELECT api.create_system('{system_name}', '{owner}',"
	+ "'{sys_type}', '{os_name}', '{comment}');")  # Query to create an object

	_interfaces = None

	system_name = None  # Name of the system
	owner = None  # Owning user (NULL for current authenticated user)
	sys_type = None  # Server, Desktop, Laptop, etc
	os_name = None  # Primary operating system
	comment = None  # Comment on the system (or NULL for no comment)
	_constraints = None

	@property
	def interfaces(self):
		self._interfaces = Interface.search(system_name=self.system_name)
		return self._interfaces

	def __init__(self, name=None, sys_type=None, osname=None, comment=None):
		self.system_name = name
		self.sys_type = sys_type
		self.os_name = osname
		self.comment = comment
		self.owner = get_username()
		self._constraints = {
				#This line grabs all the constraints on the system type and stores
				#them as a tuple, so we can check them later with:
				#for k, v in self._constraints.items():
				#	if k in self.__dict__.keys()
				#		if not self.__dict__[k] in self._constraints[k]:
				#			raise "Value not within constraints"
				"sys_type": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT type FROM systems.device_types;", results=True)),
				"os_name": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT name FROM systems.os;", results=True)),
				}
		ImpulseObject.__init__(self)
		if name and sys_type and osname:
			self.create()

	def put(self):
		if not (self.system_name and self.owner and self.sys_type and self.os_name):
			print (("Missing Parameter.\nSystem name: %s\nOwner: %s\n"
					+ "System type: %s\nOS: %s")
					% (self.system_name, self.owner, self.sys_type, self.os_name))
			return False
		if not self.comment:
			self.comment = "NULL"
		query = self.creation_query.format(system_name=self.system_name,
				owner=self.owner, sys_type=self.sys_type, os_name=self.os_name,
				comment=self.comment)
		self._conn.execute(query)
		obj = self.find(self.system_name)
		self.__dict__ = obj .__dict__
		return obj


class Interface(ImpulseObject):
	__metaclass__ = ImmutabilityMeta
	pkey = "mac"  # What parameter does the deletion query require?
	table_name = "interfaces"
	schema_name = 'systems'
	required_properties = ('name', 'mac')
	optional_properties = ('system_name', 'comment')
	removal_query = """SELECT api.remove_interface('%s');"""
	# Query that removes the object
	creation_query = """SELECT api.create_interface('{name}', '{mac}', "
			+ "{comment}');"""  # Query to create an object
	_constraints = None

	mac = None  # MAC address of the interface
	name = None
	system_name = None  # Name of the system
	comment = None  # Comment on the system (or NULL for no comment)

	def __init__(self, mac=None, name=None, system_name=None, comment=None):
		self.mac = mac
		self.name = name
		self.system_name = system_name
		self.comment = comment
		self._constraints = {
				"system_name": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT system_name FROM systems.systems;", results=True)),
				}
		ImpulseObject.__init__(self)

	def put(self):
		if not (self.system_name and self.mac):
			print ("Missing Parameter.\nSystem name: %s\nMAC: %s"
					% (self.system_name, self.mac))
			return False
		if not self.comment:
			self.comment = "NULL"
		query = self.creation_query.format(name=self.system_name, mac=self.mac,
				comment=self.comment)
		self._conn.execute(query)
		obj = self.find(self.system_name)
		self.__dict__ = obj .__dict__
		return obj
