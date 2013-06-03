# -*- coding: utf-8 -*-
from setuptools import setup


def read(filename):
    import os.path
    filename = os.path.join(os.path.dirname(__file__), filename)
    f = file(filename, 'r')
    try:
        return f.read()
    finally:
        f.close()


classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    'Natural Language :: Korean',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: Jython',
    'Topic :: Text Processing :: Filters',
]

setup(name='hypua2jamo',
      version='0.3.dev0',
      license='GNU Lesser GPL v3+',
      description='Convert Hanyang-PUA code to unicode Hangul Jamo, i.e., Syllable-Initial-Peak-Final Encoding (첫가끝 코드).',
      long_description=read('README'),
      author='mete0r',
      author_email='mete0r@sarangbang.or.kr',
      url='https://github.com/mete0r/hypua2jamo',
      classifiers=classifiers,
      packages=['hypua2jamo'],
      package_dir={'': 'src'},
      package_data={'hypua2jamo': ['*.pickle']})
