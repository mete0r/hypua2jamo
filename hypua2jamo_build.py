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
import sys

from cffi import FFI


ffi = FFI()


ffi.cdef(
    '''
int hypua_p2jc4_translate_calcsize(const unsigned int *src, int srclen);
int hypua_p2jc4_translate(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_p2jd4_translate_calcsize(const unsigned int *src, int srclen);
int hypua_p2jd4_translate(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_p2jc2_translate_calcsize(const unsigned short *src, int srclen);
int hypua_p2jc2_translate(const unsigned short *src, int srclen, unsigned short *dst);
int hypua_p2jd2_translate_calcsize(const unsigned int *src, int srclen);
int hypua_p2jd2_translate(const unsigned short *src, int srclen, unsigned short *dst);

int hypua_jc2p4_translate_calcsize(const unsigned int *src, int srclen);
int hypua_jc2p4_translate(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jc2p2_translate_calcsize(const unsigned short *src, int srclen);
int hypua_jc2p2_translate(const unsigned short *src, int srclen, unsigned short *dst);
int hypua_jd2p4_translate_calcsize(const unsigned int *src, int srclen);
int hypua_jd2p4_translate(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jd2p2_translate_calcsize(const unsigned short *src, int srclen);
int hypua_jd2p2_translate(const unsigned short *src, int srclen, unsigned short *dst);

int hypua_jc2p_translator_size();
int hypua_jc2p_translator_init(void *);
int hypua_jc2p_translator_getstate(void *);
int hypua_jc2p_translator_setstate(void *, int);
int hypua_jc2p_translator_u2_calcsize(void *, const unsigned short *src, int srclen);
int hypua_jc2p_translator_u2_calcsize_flush(void *);
int hypua_jc2p_translator_u2_translate(void *, const unsigned short *src, int srclen, unsigned short *dst);
int hypua_jc2p_translator_u2_translate_flush(void *, unsigned short *dst);
int hypua_jc2p_translator_u4_calcsize(void *, const unsigned int *src, int srclen);
int hypua_jc2p_translator_u4_calcsize_flush(void *);
int hypua_jc2p_translator_u4_translate(void *, const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jc2p_translator_u4_translate_flush(void *, unsigned int *dst);

int hypua_jd2p_translator_size();
int hypua_jd2p_translator_init(void *);
int hypua_jd2p_translator_getstate(void *);
int hypua_jd2p_translator_setstate(void *, int);
int hypua_jd2p_translator_u2_calcsize(void *, const unsigned short *src, int srclen);
int hypua_jd2p_translator_u2_calcsize_flush(void *);
int hypua_jd2p_translator_u2_translate(void *, const unsigned short *src, int srclen, unsigned short *dst);
int hypua_jd2p_translator_u2_translate_flush(void *, unsigned short *dst);
int hypua_jd2p_translator_u4_calcsize(void *, const unsigned int *src, int srclen);
int hypua_jd2p_translator_u4_calcsize_flush(void *);
int hypua_jd2p_translator_u4_translate(void *, const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jd2p_translator_u4_translate_flush(void *, unsigned int *dst);

    '''  # noqa
)


if sys.platform == 'win32':
    library = 'build/hypua2jamo-c/HanyangPUA.lib'
else:
    library = 'build/hypua2jamo-c/libHanyangPUA.a'


ffi.set_source(
    'hypua2jamo._cffi',
    '',
    extra_objects=[
        library,
    ],
)
