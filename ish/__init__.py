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

__version__ = '0.1'
CONFIG_LOCATION = "conf/ish.cfg"


def auth_info():
	"""
	Description: Get the information necessary to determine whether a user is properly logged in

	:rtype: tuple:
	:return: A tuple of the exit code of 'klist -s' and of the output of 'klist'
	"""

	import subprocess
	from tempfile import TemporaryFile
	std = TemporaryFile()
	t = subprocess.call(['klist'], stdout=std)
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
	auth= auth_info()
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


def ish_prompt(p, required=True):
	val = None
	while not val:
		val = raw_input(p)
		if not required:
			break
	return val
