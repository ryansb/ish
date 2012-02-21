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

__version__ = '0.4'
CONFIG_LOCATION = "/etc/ish.cfg"


def auth_info():
	"""
	Description: Get the information necessary to determine whether a user is
			properly logged in

	:rtype: tuple:
	:return: A tuple of the exit code of 'klist -s' and of the output of 'klist'
	"""

	import subprocess
	from tempfile import TemporaryFile
	std = TemporaryFile()
	subprocess.call(['klist'], stdout=std)
	exit_status = subprocess.call(['klist', '-s'])
	std.seek(0)
	out_lines = std.read().split('\n')
	std.close()
	ret = {}
	ret['code'] = exit_status
	for line in out_lines:
		if line.startswith('Default'):
			(ret['user'], ret['domain']) = line.lower().split(' ')[2].split('@')
	return ret


def check_auth():
	auth = auth_info()
	if auth['code'] is not 0:
		return False
	if not auth['domain'] == "csh.rit.edu":
		return False
	return True


def auth():
	auth = auth_info()
	if auth['code'] is not 0:
		return "Ticket expired or invalid. Exit and run kinit"
	if not auth['domain'] == "csh.rit.edu":
		return "Not in domain 'csh.rit.edu'"
	return "Successfully authenticated"


def get_username():
	auth = auth_info()
	if auth['code'] is not 0:
		return False
	return auth['user']


def ish_prompt(p, required=True, constraints=None):
	val = None
	while not val:
		if not constraints:
			val = raw_input(p + ": ")
		else:
			#alphabetize everything, lower case
			constraints = sorted(constraints, key=str.lower)
			opt_lists = []
			options = {}
			#create a dictionary with numbers as keys, the constraints as values
			if len(constraints) <= 30:
				options = dict(zip(range(len(constraints)), constraints))
			else:
				for count in range(int(len(constraints) / 30 + 1)):
					opt_lists.append(constraints[count * 30:count * 30 + 30])
				for segment in opt_lists:
					options[len(options)] = "%s - %s" % (segment[0], segment[-1])
			#use a lambda to make options formatted like:
			#   [0]:   this
			#   [1]:   that
			#   [2]:   other
			prompt = ("From choices:\n" + ''.join(map(lambda (k, v):
					"   [%s];   %s\n" % (k, v), options.items())) + p + ": ")
			try:
				print required
				val = int(raw_input(prompt))
			except ValueError:
				if not required:
					break
				continue
			if not val < len(options.values()):
				val = None
			elif len(constraints) <= 30:
				val = options.values()[val]
			else:
				val = ish_prompt(p, required=required, constraints=opt_lists[val])
		if not required:
			break
	return val
