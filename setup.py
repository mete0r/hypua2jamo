# -*- coding: utf-8 -*-
# hypua2jamo: Convert Hanyang-PUA code to unicode Hangul Jamo
# Copyright (C) 2012,2018 mete0r
#
# This file is part of hypua2jamo.
#
# hypua2jamo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hypua2jamo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hypua2jamo.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
from contextlib import contextmanager
from distutils.command.build import build as _build
import io
import os.path
import re
import shutil
import subprocess
import sys


def setup_dir(f):
    ''' Decorate f to run inside the directory where setup.py resides.
    '''
    setup_dir = os.path.dirname(os.path.abspath(__file__))

    def wrapped(*args, **kwargs):
        with chdir(setup_dir):
            return f(*args, **kwargs)

    return wrapped


@contextmanager
def chdir(new_dir):
    old_dir = os.path.abspath(os.curdir)
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


@setup_dir
def import_setuptools():
    try:
        import setuptools
        return setuptools
    except ImportError:
        pass

    import ez_setup
    ez_setup.use_setuptools()
    import setuptools
    return setuptools


@setup_dir
def readfile(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


@setup_dir
def get_version():
    source = readfile('src/hypua2jamo/__init__.py')
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                              source, re.M)
    if not version_match:
        raise RuntimeError('Unable to find version string.')
    return version_match.group(1)


setup_requires = readfile('requirements/setup.in')

install_requires_filename = 'requirements.in'
install_requires = readfile(install_requires_filename)

tests_require = readfile('requirements/test.in')


setup_info = {
    'name': 'hypua2jamo',
    'version': get_version(),
    'description': ('Convert Hanyang-PUA code to unicode Hangul Jamo, i.e., '
                    'Syllable-Initial-Peak-Final Encoding (첫가끝 코드).'),
    'long_description': readfile('README.rst'),
    'author': 'mete0r',
    'author_email': 'mete0r@sarangbang.or.kr',
    'license': 'GNU Lesser General Public License v3 or later (LGPLv3+)',
    'url': 'https://github.com/mete0r/hypua2jamo',
    'packages': [
        'hypua2jamo',
    ],
    # do not use '.'; just omit to specify setup.py directory
    'package_dir': {
        '': 'src',
    },
    'package_data': {
        'hypua2jamo': [
            '*.pickle',
            'jc2p.bin',
            'jd2p.bin',
            'p2jc.bin',
            'p2jd.bin',
        ],
    },
    'cffi_modules': [
        'hypua2jamo_build.py:ffi',
    ],
    'install_requires': install_requires,
    'setup_requires': setup_requires,
    'entry_points': {
        'console_scripts': [
        ],
    },
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',  # noqa
        'Natural Language :: Korean',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Text Processing :: Filters',
    ],
    'keywords': [
        'Hanyang',
        'PUA',
        'Unicode',
        'Syllable-Initial-Peak-Final Encoding',
    ],
    'zip_safe': False,
}


class build(_build):
    def run(self):
        BUILD_DIR = 'build/hypua2jamo-c'
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
        os.makedirs(BUILD_DIR)
        cwd = os.getcwd()
        os.chdir(BUILD_DIR)
        try:
            if sys.platform == 'win32':
                subprocess.check_call([
                    'cmake',
                    '-G', 'NMake Makefiles',
                    '-D', 'CMAKE_BUILD_TYPE:String=RELEASE',
                    '../../src/hypua2jamo-c'
                ])
                subprocess.check_call(['nmake'])
            else:
                subprocess.check_call([
                    'cmake',
                    '-D', 'CMAKE_BUILD_TYPE:String=RELEASE',
                    '../../src/hypua2jamo-c',
                ])
                subprocess.check_call(['make'])
        finally:
            os.chdir(cwd)
        _build.run(self)


@setup_dir
def main():
    setuptools = import_setuptools()
    setup_info['cmdclass'] = {
        'build': build,
    }
    setuptools.setup(**setup_info)


if __name__ == '__main__':
    main()
