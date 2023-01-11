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
size_t hypua_c2d_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_c2d_ucs4_encode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_c2d_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_c2d_ucs2_encode(const unsigned short *src, size_t srclen, unsigned short *dst);
size_t hypua_p2jc_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_p2jc_ucs4_encode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_p2jc_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_p2jc_ucs2_encode(const unsigned short *src, size_t srclen, unsigned short *dst);
size_t hypua_p2jd_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_p2jd_ucs4_encode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_p2jd_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_p2jd_ucs2_encode(const unsigned short *src, size_t srclen, unsigned short *dst);

size_t hypua_d2c_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_d2c_ucs4_decode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_d2c_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_d2c_ucs2_decode(const unsigned short *src, size_t srclen, unsigned short *dst);
size_t hypua_jc2p_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_jc2p_ucs4_decode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_jc2p_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_jc2p_ucs2_decode(const unsigned short *src, size_t srclen, unsigned short *dst);
size_t hypua_jd2p_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_jd2p_ucs4_decode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_jd2p_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_jd2p_ucs2_decode(const unsigned short *src, size_t srclen, unsigned short *dst);

int hypua_decoder_alloc_size();
void hypua_decoder_init_jc2p(void *decoder);
void hypua_decoder_init_jd2p(void *decoder);
void hypua_decoder_init_d2c(void *decoder);
void hypua_decoder_init(
    void *decoder,
    void *root,
    void *nodelist,
    int nodelistLen
);
int hypua_decoder_getstate(void *decoder);
int hypua_decoder_setstate(void *decoder, int state);
size_t hypua_decoder_calcsize_ucs2(void *decoder, void *src, size_t srclen);
size_t hypua_decoder_calcsize_ucs4(void *decoder, void *src, size_t srclen);
size_t hypua_decoder_calcsize_flush(void *decoder);
size_t hypua_decoder_decode_ucs2(
    void *decoder,
    void *src,
    size_t srclen,
    void *dst
);
size_t hypua_decoder_decode_ucs4(
    void *decoder,
    void *src,
    size_t srclen,
    void *dst
);
size_t hypua_decoder_decode_flush_ucs2(void *decoder, void *dst);
size_t hypua_decoder_decode_flush_ucs4(void *decoder, void *dst);

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
