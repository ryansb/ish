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


class Address(ImpulseObject):
	__metaclass__ = ImmutabilityMeta
	pkey = "address"  # What parameter does the deletion query require?
	table_name = "interface_addresses"
	schema_name = 'systems'
	required_properties = ('address', 'isprimary', 'family', 'config')
	optional_properties = ('mac', 'class', 'comment')
	removal_query = """SELECT api.remove_interface_address('%s');"""
	# Query that removes the object
	creation_query = ("""SELECT api.create_interface_address_manual(""" +
			"""'{mac}', '{address}', '{config}', '{klass}', '{isprimary}',""" +
			"""'{comment}');""")  # Query to create an object
	_constraints = None
	mac = None  # MAC address of the interface
	address = None
	config = None
	isprimary = False
	comment = None  # Comment on the system (or NULL for no comment)

	@property
	def constraints(self):
		self._constraints = {
				"system_name": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT system_name FROM systems.systems;", results=True)),
				}
		return self._constraints

	def __init__(self, mac=None, name=None, system_name=None,
			address_class=None, comment=None):
		self.mac = mac
		setattr(self, 'class', address_class)
		self.name = name
		self.system_name = system_name
		self.comment = comment
		self._constraints = {
				"system_name": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT system_name FROM systems.systems;", results=True)),
				}
		ImpulseObject.__init__(self)

	def put(self):
		try:
			self.enforce_constraints()
		except ValueError:
			return False
		if not self.comment:
			self.comment = "NULL"
		query = self.creation_query.format(mac=self.mac, address=self.address,
				config=self.config, klass=getattr(self, 'class'),
				isprimary=self.isprimary, comment=self.comment)
		self._conn.execute(query)
		obj = self.find(self.system_name)
		self.__dict__ = obj .__dict__
		return obj


class Subnet(ImpulseObject):
	__metaclass__ = ImmutabilityMeta
	pkey = "subnet"  # What parameter does the deletion query require?
	table_name = "subnets"
	schema_name = 'ip'
	required_properties = ('subnet', 'name', 'autogen', 'dhcp', 'zone',
			'owner')
	optional_properties = ('comment',)
	removal_parameter = 'subnet'
	removal_query = """SELECT api.remove_ip_subnet('%s');"""
	# Query that removes the object
	creation_query = ("""SELECT api.create_ip_subnet(""" +
			"""'{subnet}', '{name}', '{comment}', '{autogen}', '{dhcp}',""" +
			"""'{zone}', '{owner}');""")  # Query to create an object
	_constraints = None
	subnet = None  # The subnet in CIDR notation
	name = None  # The name of this subnet
	comment = None   # A comment on the subnet (or NULL for no comment)
	autogen = None  # Autopopulate the IP addresses table (adv. use only)
	dhcp = None  # TRUE to allow this subnet for DHCP, FALSE for not
	zone = None  # DNS zone to associate with this subnet
	owner = None  # The owner of the subnet (or NULL for current user)

	@property
	def constraints(self):
		self._constraints = {
				"autogen": ('TRUE', 'FALSE'),
				"dhcp": ('TRUE', 'FALSE'),
				}
		return self._constraints

	def __init__(self, subnet=None, name=None, comment=None, autogen=None,
			dhcp=None, zone=None, owner=None):
		self.subnet = subnet
		self.name = name
		self.comment = comment
		self.autogen = autogen
		self.dhcp = dhcp
		self.zone = zone
		self.owner = owner
		self._constraints = {
				"autogen": ('TRUE', 'FALSE'),
				"dhcp": ('TRUE', 'FALSE'),
				}
		ImpulseObject.__init__(self)

	def put(self):
		try:
			self.enforce_constraints()
		except ValueError:
			return False
		if not self.comment:
			self.comment = "NULL"
		query = self.creation_query.format(name=self.name,
				first_ip=self.first_ip, last_ip=self.last_ip, subnet=self.subnet,
				use=self.use, in_class=getattr(self, 'class'),
				comment=self.comment)
		self._conn.execute(query)
		obj = self.find(self.system_name)
		self.__dict__ = obj .__dict__
		return obj


class IPRange(ImpulseObject):
	__metaclass__ = ImmutabilityMeta
	pkey = "name"  # What parameter does the deletion query require?
	table_name = "ranges"
	schema_name = 'ip'
	required_properties = ('name', 'first_ip', 'last_ip', 'subnet', 'use',
			'class')
	optional_properties = ('comment',)
	removal_parameter = "name"
	removal_query = """SELECT api.remove_ip_range('%s');"""
	# Query that removes the object
	creation_query = ("""SELECT api.create_ip_range(""" +
			"""'{name}', '{first_ip}', '{last_ip}', '{subnet}', '{use}',""" +
			"""'{in_class}', '{comment}');""")  # Query to create an object
	_constraints = None
	name = None  # The name of the range
	first_ip = None  # The first IP address of the range
	last_ip = None  # The last IP address of the range
	subnet = None  # The subnet containing the range
	use = None  # A use (see documentation for uses)
	comment = None  # A comment on the range (or NULL for no comment

	def __init__(self, name=None, first_ip=None, last_ip=None, subnet=None,
			use=None, inp_class=None, comment=None):
		self.name = name
		self.first_ip = first_ip
		self.last_ip = last_ip
		self.subnet = subnet
		self.use = use
		setattr(self, 'class', inp_class)
		self.comment = comment
		ImpulseObject.__init__(self)

	def put(self):
		try:
			self.enforce_constraints()
		except ValueError:
			return False
		if not self.comment:
			self.comment = "NULL"
		query = self.creation_query.format(name=self.name,
				first_ip=self.first_ip, last_ip=self.last_ip, subnet=self.subnet,
				use=self.use, in_class=getattr(self, 'class'),
				comment=self.comment)
		self._conn.execute(query)
		obj = self.find(self.system_name)
		self.__dict__ = obj .__dict__
		return obj

	def get_unused_address(self):
		query = "SELECT api.get_address_from_range('%s');"
		addr = self._conn.execute(query % self.name, results=True)[0][0]
		return addr

#class AddressRange(ImpulseObject):
	#input_first_ip = None  # First address of the range
	#input_last_ip = None  # Last address of the range
	#input_subnet = None  # Subnet containign the range

	#def __init__(self, first_ip=None, last_ip=None, subnet=None):
		#self.input_first_ip = first_ip
		#self.input_last_ip = last_ip
		#self.input_subnet = subnet
