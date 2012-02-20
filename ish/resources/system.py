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
from ish import get_username
from ish.resources import ImpulseObject, ImmutabilityMeta, ConstraintRetriever
from ish.resources.address import Address


class System(ImpulseObject):
	"""
	Description: A System object, represents a system in Impulse
	Required properties (to be successfully saved):
		system_name: the name of the system (must be DNS-safe)
		type: The system type for a full list try System.get_constraint('type')
			Some valid ones are: Laptop, Server, Desktop, Firewall, Switch, etc...
		os_name: The name of the operating system, again, System.get_constraint
			is your friend
			Some valid ones: Windows 7, Fedora, Debian, Arch, Slackware, and Solaris

	A system has several other handy attributes
	"""

	__metaclass__ = ImmutabilityMeta
	pkey = "system_name"  # What parameter does the deletion query require?
	table_name = 'systems'
	schema_name = 'systems'
	required_properties = ('system_name', 'type', 'os_name')
	optional_properties = ('comment', )
	removal_query = """SELECT api.remove_system('%s');"""
	# Query to remove the object
	creation_query = ("SELECT api.create_system('{system_name}', '{owner}',"
	+ "'{sys_type}', '{os_name}', '{comment}');")  # Query to create an object

	_interfaces = []

	system_name = None  # Name of the system
	owner = None  # Owning user (NULL for current authenticated user)
	type = None  # Server, Desktop, Laptop, etc
	os_name = None  # Primary operating system
	comment = None  # Comment on the system (or NULL for no comment)
	_constraints = None
	_address = None
	_mac = None

	@property
	def constraints(self):
		"""
		Description: Return a dict of all the constraints for a given object
		"""
		classname = str(self.__class__).split("'")[1].split('.')[-1]
		if not self._constraints:
			self._constraints = ConstraintRetriever()
		try:
			return self._constraints[classname]
		except KeyError:
			pass
		self._constraints[classname] = {
				"type": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT type FROM systems.device_types;", results=True)),
				"os_name": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT name FROM systems.os;", results=True)),
				}
		return self._constraints[classname]

	@property
	def name(self):
		return self.system_name

	@property
	def address(self):
		"""
		Description: Calculated property based on the first address of the first
		interface. To get all addresses assigned to a system, do this instead:

		system = System.find('your_system')
		#A system can have many interfaces, loop through them
		for interface in system.interfaces:
			#since an interface can have many addresses, loop through those too
			for address_object in interface.addresses:
				print address_object.address
		"""

		if self._address:
			return self._address
		try:
			self._address = self.interfaces[0].addresses[0].address
			return self._address
		except IndexError:
			return ''
		except TypeError:
			return ''

	@property
	def mac(self):
		"""
		Description: Calculated property based on the MAC address of the first
		interface on the machine, to get all MAC addresses of interfaces on this
		system you must loop through all interfaces, or get a list of them like
		so:
			system = System.find('your_system')
			all_mac_addresses = [interface.mac for interface in system.interfaces]
		"""

		if self._mac:
			return self._mac
		try:
			self._mac = self.interfaces[0].mac
			return self._mac
		except IndexError:
			return ''
		except TypeError:
			return ''

	@property
	def interfaces(self):
		"""
		Description: Calculated property that returns a list of all interfaces
		associated with this system. If there are no interfaces, this value is a
		NoneType
		"""
		if self._interfaces:
			return self._interfaces
		self._interfaces = Interface.search(system_name=self.system_name)
		return self._interfaces

	@interfaces.setter
	def interfaces(self, value):
		self.interfaces
		if not isinstance(value, list):
			value = [value, ]
		value = filter(lambda val: isinstance(val, Interface), value)
		for val in value:
			setattr(val, 'system_name', self.system_name)
			val.constraints
			val.put()
		if self._interfaces:
			self._interfaces.extend(value)
		else:
			self.interfaces
			if not self._interfaces:
				self._interfaces = []
			self._interfaces.extend(value)

	def __init__(self, name=None, sys_type=None, osname=None, comment=None):
		"""
		Description: The constructor for System. Passing in parameters is
		allowed, but not required. Properties are only required when System.put()
		is used, as that is when the object is stored in the Impulse database
		"""
		self.system_name = name
		self.type = sys_type
		self.os_name = osname
		self.comment = comment
		self.owner = get_username()
		self.constraints
		ImpulseObject.__init__(self)
		if name and self.type and osname:
			self.create()

	def put(self):
		"""
		Description: Save the System up to the Impulse database.
		"""
		try:
			self.enforce_constraints()
		except ValueError:
			return False
		if not self.comment:
			self.comment = "NULL"
		query = self.creation_query.format(system_name=self.system_name,
				owner=self.owner, sys_type=self.type, os_name=self.os_name,
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
	creation_query = ("""SELECT api.create_interface('{sys_name}', '{mac}', """
			+ """'{name}', '{comment}');""")  # Query to create an object
	_constraints = None
	_addresses = []

	mac = None  # MAC address of the interface
	name = None
	system_name = None  # Name of the system
	comment = None  # Comment on the system (or NULL for no comment)

	@property
	def constraints(self):
		"""
		Description: Return a dict of all the constraints for a given object
		"""
		classname = str(self.__class__).split("'")[1].split('.')[-1]
		if not self._constraints:
			self._constraints = ConstraintRetriever()
		try:
			return self._constraints[classname]
		except KeyError:
			pass
		self._constraints[classname] = {
				"system_name": reduce(lambda a, b: a + b, self._conn.execute(
					"SELECT system_name FROM systems.systems;", results=True)),
				}
		return self._constraints[classname]

	@property
	def addresses(self):
		if self._addresses:
			return self._addresses
		self._addresses = Address.search(mac=self.mac)
		return self._addresses

	@addresses.setter
	def addresses(self, value):
		self.addresses
		if not isinstance(value, list):
			value = [value, ]
		value = filter(lambda val: isinstance(val, Address), value)
		for val in value:
			setattr(val, 'mac', self.mac)
			val.constraints
			val.put()
		if self._addresses:
			self._addresses.extend(value)
		else:
			self.addresses
			if not self._addresses:
				self._addresses = []
			self._addresses.extend(value)

	def __init__(self, mac=None, name=None, system_name=None, comment=None):
		self.mac = mac
		self.name = name
		self.system_name = system_name
		self.comment = comment
		self.constraints
		ImpulseObject.__init__(self)

	def put(self):
		"""
		Description: Save the System up to the Impulse database.
		"""
		try:
			self.enforce_constraints()
		except ValueError:
			return False
		if not self.comment:
			self.comment = ''
		query = self.creation_query.format(sys_name=self.system_name, mac=self.mac,
				name=self.name, comment=self.comment)
		self._conn.execute(query)
		obj = self.find(self.mac)
		self.__dict__ = obj.__dict__
		return obj
