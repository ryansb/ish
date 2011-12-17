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
points = map(lambda line; line.split()[2], lines)

def auth():
	import subprocess
	from ish import EnumAuth
	from tempfile import TemporaryFile
	std = TemporaryFile()
	exit_status = subprocess.call(['klist'], stdout=std)
	if exit_status is not 0:
		return (None, "No kerberos ticket found. Either exit and try running kinit, or use LDAP (not implemented yet)")
	else:
		std.seek(0)
		out_lines = std.read().split('\n')
		for line in out_lines:
			if line.startswith('Default'):
				(name, domain) = line.split(' ')[2].split('@')
				if not domain.lower() == "csh.rit.edu":
					return (None, "not in domain csh.rit.edu")
				u = User(name, EnumAuth(1))
				return (u, "Successfully authenticated")
	return (u, "Could not authenticate.")
