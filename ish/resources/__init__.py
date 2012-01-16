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


class ImpulseObject(object):
	removal_parameter = ""
	creation_query = ""
	removal_query = ""
	user = None
	cursor = None

	def __init__(self, user, dbcursor):
		self.user = user
		self.cursor = dbcursor

	def create(self, query):
		print """Executing query "%s" """ % query
		self.cursor.execute(query)
		self.cursor.commit()

	def remove(self):
		#run this query on the db
		query = self.removal_query % (self.__dict__[self.removal_parameter])
		print """Executing query "%s" """ % query
		self.cursor.execute(query)
		self.cursor.commit()

	def put(self, debug=False):
		"""
		Description: Saves this object to the database in its current state
		:param debug: If debug is on, will return the exact query that was run
		:type bool:

		:rtype: bool:
		:return: Returns True if save was successfull, false otherwise
		"""
		raise NotImplementedError


class DBConnection(object):
	def __init__(self, db='impulse', uname=None, passwd=None, host=None,
			port="5432"):
		import psycopg2
		self.connection = psycopg2.connect(db="impulse", user=uname,
				password=passwd, host=host)

	def api_query(self, query, results=False):
		try:
			cursor = self.connection.cursor()
			#Find the username we're authenticated to Kerberos as
			import subprocess
			from tempfile import TemporaryFile
			std = TemporaryFile()
			subprocess.Popen("""klist | grep "Default" | cut -d' ' -f3 | cut -d'@' -f1""", shell=True, stdout=std)
			std.seek(0)
			uname = std.read()

			#initialize our session in the database so we can use Impulse's
			#create/remove functions, and let Impulse deal with who's an RTP, etc
			cursor.execute("SELECT api.initialize('%s');" % uname)

			#Finally actually run our query
			cursor.execute(query)
			cursor.close()

			#commit the changes we made
			self.connection.commit()

		except Exception, e:
			raise e
		if results:
			return cursor.fetchall()
