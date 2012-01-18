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


def auth():
	import subprocess
	from tempfile import TemporaryFile
	std = TemporaryFile()
	t = subprocess.call(['klist'], stdout=std)
	exit_status = subprocess.call(['klist', '-s'])
	if exit_status is not 0:
		return (None, "No kerberos ticket found. Either exit and try running"
				+ "kinit, or use LDAP (not implemented yet)")
	else:
		std.seek(0)
		out_lines = std.read().split('\n')
		for line in out_lines:
			if line.startswith('Default'):
				(name, domain) = line.split(' ')[2].split('@')
				if not domain.lower() == "csh.rit.edu":
					return "not in domain csh.rit.edu"
				return "Successfully authenticated"
	return "Could not authenticate."


def check_auth():
	import subprocess
	from tempfile import TemporaryFile
	std = TemporaryFile()
	t = subprocess.call(['klist'], stdout=std)
	exit_status = subprocess.call(['klist', '-s'])
	if exit_status is not 0:
		return False
	else:
		std.seek(0)
		out_lines = std.read().split('\n')
		for line in out_lines:
			if line.startswith('Default'):
				(name, domain) = line.split(' ')[2].split('@')
				if not domain.lower() == "csh.rit.edu":
					return False
				return True
	return False


def get_username():
	#Find the username we're authenticated to Kerberos as
	if not check_auth():
		raise Exception("Not logged in. Please run kinit and try again")
	import subprocess
	from tempfile import TemporaryFile
	std = TemporaryFile()
	proc = subprocess.Popen("""klist | grep "Default" | cut -d' ' -f3 |"""
			+ """ cut -d'@' -f1""", shell=True, stdout=subprocess.PIPE)
	#subprocess.Popen("""klist | grep Default""", shell=True, stdout=std)
	std = proc.communicate()[0]
	return std.replace('\n', '')


def ish_prompt(p, required=True):
	val = None
	while not val:
		val = raw_input(p)
		if not required:
			break
	return val
