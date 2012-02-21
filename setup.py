#!/usr/bin/python

# Copyright (c) 2011 Ryan Brown <ryansb@csh.rit.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from setuptools import setup, find_packages

from ish import __version__

setup(name = "ish",
		version = __version__,
		description = "Impulse Shell",
		long_description="A shell to access Cohoe's Impulse registration system ( https://github.com/cohoe/impulse )",
		author = "Ryan Brown",
		author_email = "ryansb@csh.rit.edu",
		url = "https://github.com/ryansb/ish",
		packages = find_packages(),
		include_package_data = True,
		package_data = {
			'': ['conf/*.cfg'],
		},
		scripts = [
			'bin/ish',
			'bin/ipy-ish',
			'bin/impulse-quick-create',
			'bin/impulse-query',
		],
		license = 'MIT',
		platforms = 'Posix; MacOS X',
		classifiers = [ 'Development Status :: 3 - Alpha',
			'Intended Audience :: Developers',
			'License :: OSI Approved :: MIT License',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
		],
		keywords = [
			'Impulse Shell',
			'ish',
			'impulse-shell',
			'system registration',
			'csh',
		],
		dependency_links = [
		],
		install_requires = [
			'psycopg2',
		],
	)
