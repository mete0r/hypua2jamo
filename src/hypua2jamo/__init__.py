# -*- coding: utf-8 -*-
# hypua2jamo: Convert Hanyang-PUA code to unicode Hangul Jamo
# Copyright (C) 2012  mete0r
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
import sys
import logging


__version__ = '0.7'


logger = logging.getLogger(__name__)
jython = sys.platform.startswith('java')
if sys.version >= '3':
    unichr = chr


def translate(pua, composed=True):
    ''' Convert a unicode string with Hanyang-PUA codes
    to a Syllable-Initial-Peak-Final encoded unicode string.

    :param pua: a unicode string with Hanyang-PUA codes
    :param composed: the result should be composed as possible (default True)
    :return: Syllable-Initial-Peak-Final encoded unicode string
    '''

    from .encoder import PUAComposedEncoder
    from .encoder import PUADecomposedEncoder

    if composed:
        JamoEncoder = PUAComposedEncoder
    else:
        JamoEncoder = PUADecomposedEncoder
    encoder = JamoEncoder()
    return encoder.encode(pua, final=True)


def codes2unicode(codes, composed=True):
    ''' Convert Hanyang-PUA code iterable to Syllable-Initial-Peak-Final
    encoded unicode string.

    :param codes:
        an iterable of Hanyang-PUA code
    :param composed:
        the result should be composed as much as possible (default True)
    :return: Syllable-Initial-Peak-Final encoded unicode string
    '''
    pua = u''.join(unichr(code) for code in codes)
    return translate(pua, composed=composed)
