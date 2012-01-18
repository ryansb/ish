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
from ish import get_username
from ish import CONFIG_LOCATION


class ConnectionSingleton(object):
	_db_conn = None

	def __init__(self):
		super(ConnectionSingleton, self).__init__()

	@property
	def db_conn(self):
		if not self._db_conn:
			from ConfigParser import ConfigParser
			config = ConfigParser()
			config.read(CONFIG_LOCATION)
			self._db_conn = DBConnection(
					config.get('DB', 'database'),
					config.get('DB', 'user'),
					config.get('DB', 'password'),
					config.get('DB', 'host'),
					config.get('DB', 'port'))
		return self._db_conn

	def execute(self, query, results=False):
		return self.db_conn.api_query(query, results)


class DBConnection(object):
	def __init__(self, db, uname, passwd, host, port):
		import psycopg2
		self.connection = psycopg2.connect(database=db, user=uname,
				password=passwd, host=host, port=port)

	def api_query(self, query, results=False):
		try:
			cursor = self.connection.cursor()

			#initialize our session in the database so we can use Impulse's
			#create/remove functions, and let Impulse deal with who's an RTP, etc
			cursor.execute("SELECT api.initialize('%s');" % get_username())

			#Finally actually run our query
			cursor.execute(query)
			if results:
				ret = cursor.fetchall()
			cursor.close()

			#commit the changes we made
			self.connection.commit()

		except Exception, e:
			raise e
		if results:
			return ret


class ImpulseObject(object):
	_conn = ConnectionSingleton()

	def __init__(self):
		super(ImpulseObject, self).__init__()

	def remove(self, debug=False):
		#run this query on the db
		query = self.removal_query % (self.__dict__[self.pkey])
		if debug:
			print query
		self._conn.execute(query)

	@classmethod
	def find(pkey):
		#TODO: Make a generalized way of finding a certain item
		pass

	def configure(self):
		#Display prompts the user for required properties
		for prop in self.required_properties:
			self.__dict__[prop] = ish_prompt("Value for %s" % prop,
					required=True)

		#Display prompts the user for optional properties
		for prop in self.optional_properties:
			self.__dict__[prop] = ish_prompt("Value for optional property %s"
					% prop, required=False)

	def enforce_constraints(self):
		for k, v in self._constraints.items():
			if k in self.__dict__.keys():
				if not (self.__dict__[k] and self.__dict__[k]
						in self._constraints[k]):
					raise Exception("Value '%s' is not within constraints for'%s'"
							% (self.__dict__[k], k))
