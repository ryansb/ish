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
from psycopg2 import InternalError


class ImpulseDBError(Exception):
	"""
	Description: Raised whenever an Impulse query is rejected, typically because
	some data does not validate.
	"""
	def __init__(self, message):
		# Call the base class constructor with the parameters it needs
		Exception.__init__(self, message)


class ConnectionSingleton(object):
	_db_conn = None

	def __init__(self):
		"""
		Description: A singleton to manage database connection.

		It reads authentication information from the Impulse Shell configuration
		file, which is located in /etc/ish.cfg
		"""
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
		try:
			return self.db_conn.api_query(query, results)
		except InternalError, e:
			raise ImpulseDBError(e.message)
		finally:
			self._db_conn = None


class DBConnection(object):
	def __init__(self, dbname, uname, passwd, host, port):
		"""
		Description: A connection to PGSQL to run queries on.
		"""
		import psycopg2
		self.dbname = dbname
		self.uname = uname
		self.passwd = passwd
		self.host = host
		self.port = port
		self.connection = psycopg2.connect(database=dbname, user=uname,
				password=passwd, host=host, port=port)

	def api_query(self, query, results=False):
		"""
		Description: Run a query on the PGSQL connection. By default, no results
		are returned. If results are desired/needed then be sure to call as:
			api_query(query, results=True)
		"""
		try:
			if self.connection.closed:
				import psycopg2
				self.connection = psycopg2.connect(database=self.dbname,
						user=self.uname, password=self.passwd, host=self.host, port=self.port)
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
			self.connection.close()

		except Exception, error:
			raise error
		if results:
			return ret


def singleton(cls):
	"""
	A decorator to make a class into a singleton.

	When a class is wrapped in this decorator, this decorator will always make
	any calls on that class (or an instance of it) goes to the same instance of
	a given class.

	See PEP 318 for clarification.
	http://www.python.org/dev/peps/pep-0318/#examples
	"""
	instances = {}
	def getinstance():
		if cls not in instances:
			instances[cls] = cls()
		return instances[cls]
	return getinstance


@singleton
class ConstraintRetriever(dict):
	pass


class ImmutabilityMeta(type):
	"""A metaclass to prevent the alteration of certain key attributes that
	shouldn't be messed with."""

	def __setattr__(cls, name, value):
		"""
		Description: Override the setattr method on any inheriting classes such
		that certain properties cannot be altered, because that would break
		stuff.
		"""
		immutables = ('table_name', 'schema_name', 'required_properties',
				'optional_properties', 'pkey', 'removal_query', 'creation_query')
		if name in immutables:
			raise AttributeError("Cannot modify .%s" % name)
		return type.__setattr__(cls, name, value)

	def __delattr__(cls, name):
		"""
		Description: Override the delattr method on any inheriting classes such
		that certain properties cannot be deleted, because that would break
		stuff.
		"""
		immutables = ('table_name', 'schema_name', 'required_properties',
				'optional_properties', 'pkey', 'removal_query', 'creation_query')
		if name in immutables:
			raise AttributeError("Cannot delete .%s" % name)
		return type.__delattr__(cls, name)


class ImpulseObject(object):
	_conn = ConnectionSingleton()
	__metaclass__ = ImmutabilityMeta

	def __init__(self):
		"""
		Description: Parent Impulse Object, all other objects inherit from this
		one and it provides things like immutable attributes, the put() method,
		and the find() and search() methods. There should never be a reason to
		instantiate a plain ImpulseObject, as it can't actually do anything on
		its own.
		"""
		if str(self.__class__) == "<class 'ish.resources.ImpulseObject'>":
			raise NotImplementedError("This is a parent class.")

	def remove(self, debug=False):
		"""
		Description: Delete this object from the database.
		This operation is not undoable, period. Be careful
		"""
		#run this query on the db
		query = self.removal_query % (self.__dict__[self.pkey])
		if debug:
			print query
		self._conn.execute(query)

	@classmethod
	def find(cls, pkey):
		"""Return a single object based on the primary key for the objects in
		that table"""
		if isinstance(cls, ImpulseObject):
			raise NotImplementedError("Can't run this on a generic" +
					" ImpulseObject.")
		column_query = ("""select * from information_schema.columns""" +
				""" where table_name = '%s'""")
		# Get all the columns in the specified table
		column_result = cls._conn.execute(column_query % cls.table_name,
				results=True)
		if not column_result:
			raise Exception("Cannot find table %s" % cls.table_name)
		# pull only the column names using list comprehension
		columns = [res[3] for res in column_result]

		obj_query = """select * from %s.%s where %s = '%s'"""
		obj = cls._conn.execute(obj_query % (cls.schema_name, cls.table_name,
				cls.pkey, pkey), results=True)
		if not obj:
			raise Exception("Cannot find object %s with key %s" %
					(pkey, cls.pkey))

		result = cls()
		for col, val in zip(columns, obj[0]):
			result.__dict__[col] = val
		return result

	@classmethod
	def all(cls):
		"""
		Description: Get every single object of a given type. This is a
		generator ( http://docs.python.org/tutorial/classes.html#generators ) and
		should be used like this:
			all_systems = System.all()
			first_system = s.next()

		When a generator has run out of items, it raises a StopIteration error.
		Using a generator is much faster that returning a (potentially large)
		list containing all of a particular type of object.
		"""
		if isinstance(cls, ImpulseObject):
			raise NotImplementedError("Can't run this on a generic" +
					" ImpulseObject.")
		column_query = ("""select * from information_schema.columns""" +
				""" where table_name = '%s'""")
		# Get all the columns in the specified table
		column_result = cls._conn.execute(column_query % cls.table_name,
				results=True)
		if not column_result:
			raise Exception("Cannot find table %s" % cls.table_name)
		# pull only the column names using list comprehension
		columns = [res[3] for res in column_result]

		obj_query = """select * from %s.%s;"""
		res = cls._conn.execute(obj_query % (cls.schema_name, cls.table_name),
				results=True)
		if not res:
			raise Exception("No results for query %s" % obj_query)

		for item in res:
			obj = cls()
			for col, val in zip(columns, item):
				obj.__dict__[col] = val
			yield obj

	@classmethod
	def search(cls, **kwargs):
		"""Return a list objects that match parameters that aren't primary
		keys

		For example: object.search(owner=some1, type=atype)

		It is possible to specify many parameters, as long as they are all valid
		"""
		if len(kwargs.items()) < 1:
			raise Exception("This function requires search parameters")
		if isinstance(cls, ImpulseObject):
			raise NotImplementedError("Can't run this on a generic" +
					" ImpulseObject.")
		column_query = ("""select * from information_schema.columns""" +
				""" where table_name = '%s'""")
		# Get all the columns in the specified table
		column_result = cls._conn.execute(column_query % cls.table_name,
				results=True)
		if not column_result:
			raise Exception("Cannot find table %s" % cls.table_name)
		# pull only the column names using list comprehension
		columns = [res[3] for res in column_result]

		obj_query = """select * from %s.%s where %s = '%s' """
		additional = ''
		for key, val in kwargs.items()[1:]:
			additional += "and %s = '%s' " % (key, val)
		additional += ';'
		res = cls._conn.execute(obj_query % (cls.schema_name, cls.table_name,
			kwargs.items()[0][0], kwargs.items()[0][1]) + additional, results=True)
		if not res:
			return None

		results = []
		for item in res:
			obj = cls()
			for col, val in zip(columns, item):
				obj.__dict__[col] = val
			results.append(obj)
		return results

	def get_constraint(self, attr):
		"""
		Description: Get all allowed values for a particular attribute. Great for
		if you need to present all those options to a user, or are just curious
		yourself. Used because hardcoding most values is not feasible, such as
		valid usernames.
		"""
		try:
			classname = str(self.__class__).split("'")[1].split('.')[-1]
			return self._constraints[classname][attr]
		except KeyError:
			return ()

	def configure(self):
		"""
		Description: Creates a series of prompts asking for values, and specifies
		which are optional and which are not. Only use in places where user has
		the ability to get data to STDIN.
		"""
		classname = str(self.__class__).split("'")[1].split('.')[-1]
		#Display prompts the user for required properties
		for prop in self.required_properties:
			if prop in self._constraints[classname]:
				self.__dict__[prop] = ish_prompt("Value for %s" % prop,
						required=True, constraints=self._constraints[classname][prop])
			else:
				self.__dict__[classname][prop] = ish_prompt("Value for %s" % prop,
						required=True)

		#Display prompts the user for optional properties
		for prop in self.optional_properties:
			if prop in self._constraints[classname]:
				self.__dict__[prop] = ish_prompt("Value for optional property %s" %
						prop, required=False, constraints=self._constraints[classname][prop])
			else:
				self.__dict__[prop] = ish_prompt("Value for optional property %s" %
						prop, required=False)

	def enforce_constraints(self):
		"""
		Description: Enforce all constraints on properties that have them. If a
		value is not within the given constraints, then a ValueError exception is
		raised. It is good to check this before saving an object to the database.
		"""
		classname = str(self.__class__).split("'")[1].split('.')[-1]
		for key in list(set(self._constraints[classname].keys()) &
				set(self.__dict__.keys())):
			if self.__dict__[key] not in self._constraints[classname][key]:
				raise ValueError("Value '%s' is not within constraints for'%s'" %
						(self.__dict__[key], key))

	@property
	def formatted_date_modified(self):
		from datetime import datetime
		if self.date_modified.strftime("%D") == datetime.now().strftime("%D"):
			return self.date_modified.strftime("%H:%M")
		return self.date_modified.strftime("%Y-%m-%d")

	def __repr__(self):
		if self.name:
			return self.name
		else:
			return object.__repr__(self)
