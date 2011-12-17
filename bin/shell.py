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


import sys
sys.path.insert(0,".")
from ish import auth
from pkg_resources import resource_listdir

OBJS = []
current_user = None

class Ls(object):
	def __repr__(self):
		return self.__call__()
	def __call__(self):
		return "\n".join(OBJS)

class Auth(object):
	def __repr__(self):
		return self.__call__()

	def __call__(self):
		(user, msg) = auth()


if __name__ == "__main__":
	#do something about logging sometime
	from ish.resources.System import System
	import code
	import readline
	local = {"System": System}
	sys.ps1 = "\x01\x1b[34m\x1b[1m\x02>>> \x01\x1b[0m\x02"
	sys.ps2 = "... "
	for f in resource_listdir("ish.resources", ""):
		if f.endswith(".py"):
			m = f.split(".")[0]
			if m != "__init__":
				__import__("ish.resources.%s" % m)

	OBJS = local.keys()
	local["ls"] = Ls()
	local["auth"] = Auth()
	code.interact(banner="Impulse Shell\nUse Ctrl+D to exit\nls prints all loaded classes", local=local)





