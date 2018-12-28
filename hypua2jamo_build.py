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
from __future__ import unicode_literals
from __future__ import print_function

from cffi import FFI


ffi = FFI()


ffi.cdef(
    '''
int hypua_p2jc4_translate_calcsize(const uint32_t *src, int srclen);
int hypua_p2jc4_translate(const uint32_t *src, int srclen, uint32_t *dst);
int hypua_p2jd4_translate_calcsize(const uint32_t *src, int srclen);
int hypua_p2jd4_translate(const uint32_t *src, int srclen, uint32_t *dst);
    '''  # noqa
)


ffi.set_source(
    'hypua2jamo._p2j4',
    '#include <inttypes.h>',
    extra_objects=[
        'lib/p2j4.a',
    ],
)
