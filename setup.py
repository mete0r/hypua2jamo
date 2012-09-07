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


setup(name='hypua2jamo',
      version='0.1',
      license='GNU Lesser GPL v3',
      description='Convert Hanyang-PUA code to unicode Hangul Jamo, i.e., Syllable-Initial-Peak-Final Encoding (첫가끝 코드).',
      long_description=read('README'),
      author='mete0r',
      author_email='mete0r@sarangbang.or.kr',
      url='https://github.com/mete0r/hypua2jamo',
      packages=['hypua2jamo'],
      package_dir={'': 'src'})
