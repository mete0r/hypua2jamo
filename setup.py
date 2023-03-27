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
from distutils.errors import CCompilerError
from distutils.errors import DistutilsExecError
from distutils.errors import DistutilsPlatformError
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
    'long_description': readfile('README.rst') + '\n' + readfile('CHANGES.rst'),  # noqa
    'long_description_content_type': 'text/x-rst',
    'author': 'mete0r',
    'author_email': '137794+mete0r@users.noreply.github.com',
    'license': 'GNU Lesser General Public License v3 or later (LGPLv3+)',
    'url': 'https://github.com/mete0r/hypua2jamo',
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*,!=3.6.*',  # noqa
    'packages': [
        'hypua2jamo',
    ],
    # do not use '.'; just omit to specify setup.py directory
    'package_dir': {
        '': 'src',
    },
    'package_data': {
        'hypua2jamo': [
            'c2d.bin',
            'd2c.bin',
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
            'hypua2jamo = hypua2jamo.cli:main',
        ],
    },
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',  # noqa
        'Natural Language :: Korean',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
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


@setup_dir
def main():
    setuptools = import_setuptools()
    from setuptools.extension import Extension
    from setuptools.command.build_ext import build_ext

    class optional_build_ext(build_ext):
        '''
        This class subclasses build_ext and allows
        the building of C extensions to fail.
        '''
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
            except Exception as e:
                print('*' * 80)
                print(e)
                print()
                print(
                    'WARNING: An optional C module (hypua2jamo-c) '
                    'could not be built. Optimization for this package '
                    'will not be available!'
                )
                print('*' * 80)
            finally:
                os.chdir(cwd)

            try:
                build_ext.run(self)
            except DistutilsPlatformError as e:
                self._unavailable(e)

        def build_extension(self, ext):
            try:
                build_ext.build_extension(self, ext)
            except (CCompilerError, DistutilsExecError, OSError) as e:
                self._unavailable(e)

        def _unavailable(self, e):
            print('*' * 80)
            print(e)
            print()
            print(
                'WARNING: An optional code optimization (C extension) '
                'could not be built. Optimization for this package '
                'will not be available!'
            )
            print('*' * 80)

    setup_info['cmdclass'] = {
        'build_ext': optional_build_ext,
    }

    if sys.platform == 'win32':
        library = 'build/hypua2jamo-c/HanyangPUA.lib'
    else:
        library = 'build/hypua2jamo-c/libHanyangPUA.a'

    setup_info['ext_modules'] = [
        Extension('hypua2jamo._cython', [
            'src/hypua2jamo/_cython' + str(sys.version_info.major) + '.c'
        ], include_dirs=[
            'src/hypua2jamo-c',
        ], extra_objects=[
            library,
        ])
    ]
    setuptools.setup(**setup_info)


if __name__ == '__main__':
    main()
