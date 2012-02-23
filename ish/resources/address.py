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
from ish import ish_prompt
from psycopg2 import IntegrityError
from ish.resources import ImpulseObject, ImmutabilityMeta, ConstraintRetriever


class Address(ImpulseObject):
	"""
	Description: The Address object, contains an address, what DNS family the
	address is in, and how the address is assigned (static, dhcp, etc.)
	"""
	__metaclass__ = ImmutabilityMeta
	pkey = "address"  # What parameter does the deletion query require?
	table_name = "interface_addresses"
	schema_name = 'systems'
	required_properties = ('address', 'isprimary', 'family', 'config')
	optional_properties = ('mac', 'class', 'comment')
	# Query that removes the object
	removal_query = """SELECT api.remove_interface_address('%s');"""
	modification_query = ("SELECT api.modify_interface_address('{address}', '{field}', '{val}')")
	creation_query = ("""SELECT api.create_interface_address(""" +
			"""'{mac}', '{address}', '{config}', '{klass}', '{isprimary}',""" +
			"""'{comment}');""")  # Query to create an object
	_constraints = None
	mac = None  # MAC address of the interface
	address = None
	config = None
	family = None
	isprimary = False
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
				"config": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT config FROM dhcp.config_types;", results=True)),
				"class": reduce(lambda a, b: a + b, self._conn.execute(
						"SELECT class FROM dhcp.classes;", results=True)),
				}
		return self._constraints[classname]

	def __init__(self, mac=None, name=None, family=None,
			address_class=None, config=None, comment=None):
		"""
		Description: Create an Address object, can accept arguments or not
		"""
		self.mac = mac
		setattr(self, 'class', address_class)
		if not address_class:
			setattr(self, 'class', 'default')
		self.name = name
		self.family = family
		self.config = config
		self.comment = comment
		self.constraints
		ImpulseObject.__init__(self)

	def put(self):
		"""
		Description: Save the Address object to the Impulse database
		"""
		self.enforce_constraints()
		try:
			self.enforce_constraints()
		except ValueError:
			return False
		if not self.comment:
			self.comment = "NULL"
		query = self.creation_query.format(mac=self.mac, address=self.address,
				config=self.config, klass=getattr(self, 'class'),
				isprimary=self.isprimary, comment=self.comment)
		try:
			self._conn.execute(query)
		except IntegrityError:
			for key in self.optional_properties + self.required_properties:
				query = self.modification_query.format(address=self.address, field=key, val=self.__dict__[key])
				self._conn.execute(query)
		obj = self.find(self.address)
		self.__dict__ = obj .__dict__
		return obj

	def use_unused_address(self, ipr=None):
		"""
		Description: Grab an unused address from an IPRange, specified by its name
		If no parameters are given, it puts up a prompt to ask for the IPRange to use
		If an IPRange object is given, it gets the address from that object
		If a string is given, it gets the IPRange with the name specified
		returns the address that was used, and assigns the free address to the
		"Address.address" attribute
		"""
		if not ipr:
			ipr = ish_prompt("Select an IP Range", constraints=[i.name for i in IPRange.all()])
		if not isinstance(IPRange, ipr):
			iprange = IPRange.find(ipr)
		else: iprange = ipr
		self.address = iprange.get_unused_address()
		return self.address


class Subnet(ImpulseObject):
	"""
	Description: A Subnet object, including the address range
	"""
	__metaclass__ = ImmutabilityMeta
	pkey = "subnet"  # What parameter does the deletion query require?
	table_name = "subnets"
	schema_name = 'ip'
	required_properties = ('subnet', 'name', 'autogen', 'dhcp', 'zone',
			'owner')
	optional_properties = ('comment',)
	removal_parameter = 'subnet'
	# Query that removes the object
	removal_query = """SELECT api.remove_ip_subnet('%s');"""
	modification_query = ("SELECT api.modify_ip_subnet('{subnet}', '{field}', '{val}')")
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
				"autogen": ('TRUE', 'FALSE'),
				"dhcp": ('TRUE', 'FALSE'),
				}
		return self._constraints[classname]

	def __init__(self, subnet=None, name=None, comment=None, autogen=None,
			dhcp=None, zone=None, owner=None):
		"""
		Description: Create a Subnet object, can accept arguments or not
		"""
		self.subnet = subnet
		self.name = name
		self.comment = comment
		self.autogen = autogen
		self.dhcp = dhcp
		self.zone = zone
		self.owner = owner
		self.constraints
		ImpulseObject.__init__(self)

	def put(self):
		"""
		Description: Save this object to the Impulse database
		"""
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
		try:
			self._conn.execute(query)
		except IntegrityError:
			for key in self.optional_properties + self.required_properties:
				query = self.modification_query.format(subnet=self.subnet, field=key, val=self.__dict__[key])
				self._conn.execute(query)
		obj = self.find(self.system_name)
		self.__dict__ = obj .__dict__
		return obj


class IPRange(ImpulseObject):
	"""
	Description: an IPRange object, which only contains a first and last IP,
	along with their subnet and a description of what they are intended to be
	used for.
	"""
	__metaclass__ = ImmutabilityMeta
	pkey = "name"  # What parameter does the deletion query require?
	table_name = "ranges"
	schema_name = 'ip'
	required_properties = ('name', 'first_ip', 'last_ip', 'subnet', 'use',
			'class')
	optional_properties = ('comment',)
	removal_parameter = "name"
	# Query that removes the object
	removal_query = """SELECT api.remove_ip_range('%s');"""
	modification_query = ("SELECT api.modify_ip_range('{name}', '{field}', '{val}')")
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
		"""
		Description: Instantiate an IPRange object, does not require parameters
		to be given.
		"""
		self.name = name
		self.first_ip = first_ip
		self.last_ip = last_ip
		self.subnet = subnet
		self.use = use
		setattr(self, 'class', inp_class)
		self.comment = comment
		ImpulseObject.__init__(self)

	def put(self):
		"""
		Description: Save the IPRange object to the Impulse database
		"""
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
		try:
			self._conn.execute(query)
		except IntegrityError:
			for key in self.optional_properties + self.required_properties:
				query = self.modification_query.format(name=self.name, field=key, val=self.__dict__[key])
				self._conn.execute(query)
		obj = self.find(self.system_name)
		self.__dict__ = obj .__dict__
		return obj

	def get_unused_address(self):
		"""
		Description: Returns the first unused address in a given IPRange. If
		there is no unused address, raises ImpulseError.
		"""
		query = "SELECT api.get_address_from_range('%s');"
		# If there are no unused addresses, this will throw an ImpulseError
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
