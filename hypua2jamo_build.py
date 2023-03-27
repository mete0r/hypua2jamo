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


c_declarations = '''
/* encoder */

size_t hypua_c2d_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_c2d_ucs4_encode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_c2d_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_c2d_ucs2_encode(const uint16_t *src, size_t srclen, uint16_t *dst);
size_t hypua_p2jc_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_p2jc_ucs4_encode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_p2jc_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_p2jc_ucs2_encode(const uint16_t *src, size_t srclen, uint16_t *dst);
size_t hypua_p2jd_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_p2jd_ucs4_encode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_p2jd_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_p2jd_ucs2_encode(const uint16_t *src, size_t srclen, uint16_t *dst);

/* decoder */

size_t hypua_d2c_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_d2c_ucs4_decode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_d2c_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_d2c_ucs2_decode(const uint16_t *src, size_t srclen, uint16_t *dst);
size_t hypua_jc2p_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_jc2p_ucs4_decode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_jc2p_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_jc2p_ucs2_decode(const uint16_t *src, size_t srclen, uint16_t *dst);
size_t hypua_jd2p_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_jd2p_ucs4_decode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_jd2p_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_jd2p_ucs2_decode(const uint16_t *src, size_t srclen, uint16_t *dst);

/* decoder generic */

int hypua_decoder_alloc_size();
void hypua_decoder_init_d2c(void *decoder);
void hypua_decoder_init_jc2p(void *decoder);
void hypua_decoder_init_jd2p(void *decoder);
void hypua_decoder_init(
		void *decoder,
		const void *root,
		const void *nodelist,
		int nodelistLen
);
int hypua_decoder_getstate(void *decoder);
int hypua_decoder_setstate(void *decoder, int state);
size_t hypua_decoder_calcsize_ucs2(void *decoder, const uint16_t *src, size_t srclen);
size_t hypua_decoder_calcsize_ucs4(void *decoder, const uint32_t *src, size_t srclen);
size_t hypua_decoder_calcsize_flush(void *decoder);
size_t hypua_decoder_decode_ucs2(
		void *decoder,
		uint16_t *src,
		size_t srclen,
		uint16_t *dst
);
size_t hypua_decoder_decode_ucs4(
		void *decoder,
		uint32_t *src,
		size_t srclen,
		uint32_t *dst
);
size_t hypua_decoder_decode_flush_ucs2(void *decoder, void *dst);
size_t hypua_decoder_decode_flush_ucs4(void *decoder, void *dst);
'''


ffi.cdef(
    c_declarations,
)


if sys.platform == 'win32':
    library = 'build/hypua2jamo-c/HanyangPUA.lib'
else:
    library = 'build/hypua2jamo-c/libHanyangPUA.a'


ffi.set_source(
    'hypua2jamo._cffi',
    c_declarations,
    extra_objects=[
        library,
    ],
)

if __name__ == '__main__':
    ffi.compile(verbose=True)
