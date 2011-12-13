#!/usr/bin/env python
# -*- coding; utf-8 -*-
# Author: Ryan Brown
# Description: #
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

class EnumAuth(object):
	Admin = 0
	User = 1
	NoAuth = 2
	Test = 3
	def __init__(self, Type):
		self.value = Type

	def __str__(self):
		if self.value == EnumAuth.Admin:
			return 'Admin'
		if self.value == EnumAuth.User:
			return 'User'
		if self.value == EnumAuth.NoAuth:
			return 'NoAuth'
		if self.value == EnumAuth.Test:
			return 'Test'

	def __eq__(self,y):
		return self.value==y.value


class ImpulseObject(object):
	removal_parameter = ""
	pass

	def create(self):
		pass

	def remove(self):
		self.__dict__[self.removal_parameter]
		pass
