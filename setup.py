#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN -- http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import versioneer
versioneer.versionfile_source = 'tvd/_version.py'
versioneer.versionfile_build = 'tvd/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'tvd-'

try:
    from ez_setup import use_setuptools
    use_setuptools()
except:
    pass

from setuptools import setup, find_packages

setup(
    name='tvd',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='TVD: A Reproducible and Multiply Aligned TV Series Dataset',
    author='Hervé Bredin',
    author_email='bredin@limsi.fr',
    url='https://github.com/tvd-dataset/tvd',
    packages=find_packages(),
    install_requires=[
        'pyannote.core >= 0.2',
        'simplejson >= 3.4.1',
        'lxml >=2.3.4',
        'numpy >=1.7.1',
        'PyYAML >= 3.10',
        'path.py >= 5.1',
        'docopt >= 0.6.1',
        'requests >= 2.2.1',
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering"
    ]
)
