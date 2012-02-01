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
	optional_properties = ('mac','class', 'comment')
	removal_query = """SELECT api.remove_interface_address('%s');"""
	# Query that removes the object
	creation_query = ("""SELECT api.create_interface_address_manual(""" +
			"""'{mac}', '{address}', '{config}', '{class}', '{isprimary}',""" +
			"""'{comment}');""") # Query to create an object
	_constraints = None
	_addresses = []

	mac = None  # MAC address of the interface
	address = None
	#__dict__['class'] = None
	config = None
	isprimary = False
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


class Subnet(ImpulseObject):
	input_subnet = None  # The subnet in CIDR notation
	input_name = None  # The name of this subnet
	input_comment = None   # A comment on the subnet (or NULL for no comment)
	input_autogen = None  # Autopopulate the IP addresses table (adv. use only)
	input_dhcp = None  # TRUE to allow this subnet for DHCP, FALSE for not
	input_zone = None  # DNS zone to associate with this subnet
	input_owner = None  # The owner of the subnet (or NULL for current user)
	removal_parameter = "input_subnet"

	def __init__(self, subnet=None, name=None, comment=None, autogen=None,
			dhcp=None, zone=None, owner=None):
		self.input_subnet = subnet
		self.input_name = name
		self.input_comment = comment
		self.input_autogen = autogen
		self.input_dhcp = dhcp
		self.input_zone = zone
		self.input_owner = owner


class IPRange(ImpulseObject):
	input_name = None  # The name of the range
	input_first_ip = None  # The first IP address of the range
	input_last_ip = None  # The last IP address of the range
	input_subnet = None  # The subnet containing the range
	input_use = None  # A use (see documentation for uses)
	input_class = None  # The DHCP class of the range.
		#NOTE: input_class of NULL will allow unknown clients to get a lease
	input_comment = None  # A comment on the range (or NULL for no comment
	removal_parameter = "input_name"

	def __init__(self, name=None, first_ip=None, last_ip=None, subnet=None,
			use=None, inp_class=None, comment=None):
		self.input_name = name
		self.input_first_ip = first_ip
		self.input_last_ip = last_ip
		self.input_subnet = subnet
		self.input_use = use
		self.input_class = inp_class
		self.input_comment = comment


class AddressRange(ImpulseObject):
	input_first_ip = None  # First address of the range
	input_last_ip = None  # Last address of the range
	input_subnet = None  # Subnet containign the range

	def __init__(self, first_ip=None, last_ip=None, subnet=None):
		self.input_first_ip = first_ip
		self.input_last_ip = last_ip
		self.input_subnet = subnet
