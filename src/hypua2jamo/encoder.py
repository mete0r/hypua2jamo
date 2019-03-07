# -*- coding: utf-8 -*-
# hypua2jamo: Convert Hanyang-PUA code to unicode Hangul Jamo
# Copyright (C) 2012,2018-2019  mete0r
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
from __future__ import print_function
from array import array
from codecs import IncrementalEncoder
from struct import Struct
import io
import os.path

try:
    from cffi import FFI
    from hypua2jamo._cffi import lib as _cffi
except ImportError:
    cffi_available = False
else:
    cffi_available = True

try:
    from . import _cython
except ImportError:
    cython_available = False
else:
    cython_available = True


_UNICODE_SIZE = array('u').itemsize
try:
    unichr
except NameError:
    # for Python 3
    unichr = chr

pua_groups_length_struct = Struct('<I')
group_entry_struct = Struct('<HH')
jamo_length_struct = Struct('<H')
jamo_struct = Struct('<H')


def read_struct(fp, struct):
    data = fp.read(struct.size)
    if len(data) != struct.size:
        raise Exception()
    return struct.unpack(data)


def load_pack_fp(fp):
    pua_groups_length = read_struct(fp, pua_groups_length_struct)[0]

    pua_groups = [
        read_struct(fp, group_entry_struct)
        for i in range(0, pua_groups_length)
    ]

    p2j_mapping = []

    for pua_start, pua_end in pua_groups:
        jamo_seq_list = []
        for pua_code in range(pua_start, pua_end + 1):
            jamo_code_list = []
            jamo_length = read_struct(fp, jamo_length_struct)[0]
            for i in range(jamo_length):
                jamo_code = read_struct(fp, jamo_struct)[0]
                jamo_code_list.append(jamo_code)
            jamo_seq = ''.join(
                unichr(jamo_code) for jamo_code in jamo_code_list
            )
            jamo_seq_list.append(jamo_seq)
        p2j_mapping.append(
            (pua_start, pua_end, tuple(jamo_seq_list))
        )
    return tuple(p2j_mapping)


def load_pack(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    with io.open(filename, 'rb') as fp:
        return load_pack_fp(fp)


c2d_mapping = load_pack('c2d.bin')
p2jc_mapping = load_pack('p2jc.bin')
p2jd_mapping = load_pack('p2jd.bin')


def lookup(mapping, pua_code):
    for pua_start, pua_end, jamo_seq_list in mapping:
        if pua_start <= pua_code <= pua_end:
            return jamo_seq_list[pua_code - pua_start]
    return unichr(pua_code)


class JamoEncoderImplementationOnPurePython(
    IncrementalEncoder
):

    def encode(self, pua_string, final=False):
        mapping = self.mapping
        return ''.join(
            lookup(mapping, ord(pua_chr))
            for pua_chr in pua_string
        )

    def reset(self):
        pass

    def getstate(self):
        return 0

    def setstate(self, state):
        pass


class ComposedJamoEncoderImplementationOnPurePython(
    JamoEncoderImplementationOnPurePython
):
    '''
    PUA-to-Jamo(composed) encoder

    Pure python implementation.
    '''

    mapping = p2jc_mapping


class DecomposedJamoEncoderImplementationOnPurePython(
    JamoEncoderImplementationOnPurePython
):
    '''
    PUA-to-Jamo(decomposed) encoder

    Pure python implementation.
    '''

    mapping = p2jd_mapping


class DecomposingEncoderImplementationOnPurePython(
    JamoEncoderImplementationOnPurePython
):
    '''
    Jamo(composed)-to-Jamo(decomposed) encoder

    Pure python implementation.
    '''

    mapping = c2d_mapping


def encode_to_composed(pua_string):
    return ''.join(
        lookup(p2jc_mapping, ord(pua_chr))
        for pua_chr in pua_string
    )


def encode_to_decomposed(pua_string):
    return ''.join(
        lookup(p2jd_mapping, ord(pua_chr))
        for pua_chr in pua_string
    )


class JamoEncoderImplementationOnCFFI(
    IncrementalEncoder
):

    def reset(self):
        pass

    def getstate(self):
        return 0

    def setstate(self, state):
        pass

    def encode(self, pua_string, final=False):
        ffi = self._ffi

        pua_array = array('u', pua_string)
        pua_ptr, pua_len = pua_array.buffer_info()
        pua_ptr = ffi.cast('void *', pua_ptr)

        jamo_size = self._calcsize(pua_ptr, pua_len)

        jamo_array = array('u', u' '*jamo_size)
        jamo_ptr = jamo_array.buffer_info()[0]
        jamo_ptr = ffi.cast('void *', jamo_ptr)
        jamo_len = self._encode(pua_ptr, pua_len, jamo_ptr)
        if jamo_size != jamo_len:
            raise Exception(
                'p2jcx translation failed', jamo_size, jamo_len
            )
        return jamo_array.tounicode()


class ComposedJamoEncoderImplementationOnCFFI(
    JamoEncoderImplementationOnCFFI
):
    '''
    PUA-to-Jamo(composed) encoder

    CFFI implementation.
    '''

    def __init__(self, errors='strict'):
        IncrementalEncoder.__init__(self, errors)

        self._ffi = FFI()

        if _UNICODE_SIZE == 4:
            self._calcsize = _cffi.hypua_p2jc_ucs4_calcsize
            self._encode = _cffi.hypua_p2jc_ucs4_encode
        elif _UNICODE_SIZE == 2:
            self._calcsize = _cffi.hypua_p2jc_ucs2_calcsize
            self._encode = _cffi.hypua_p2jc_ucs2_encode
        else:
            raise AssertionError(_UNICODE_SIZE)


class DecomposedJamoEncoderImplementationOnCFFI(
    JamoEncoderImplementationOnCFFI
):
    '''
    PUA-to-Jamo(decomposed) encoder

    CFFI implementation.
    '''

    def __init__(self, errors='strict'):
        IncrementalEncoder.__init__(self, errors)

        self._ffi = FFI()

        if _UNICODE_SIZE == 4:
            self._calcsize = _cffi.hypua_p2jd_ucs4_calcsize
            self._encode = _cffi.hypua_p2jd_ucs4_encode
        elif _UNICODE_SIZE == 2:
            self._calcsize = _cffi.hypua_p2jd_ucs2_calcsize
            self._encode = _cffi.hypua_p2jd_ucs2_encode
        else:
            raise AssertionError(_UNICODE_SIZE)


class DecomposingEncoderImplementationOnCFFI(
    JamoEncoderImplementationOnCFFI
):
    '''
    PUA-to-Jamo(decomposed) encoder

    CFFI implementation.
    '''

    def __init__(self, errors='strict'):
        IncrementalEncoder.__init__(self, errors)

        self._ffi = FFI()

        if _UNICODE_SIZE == 4:
            self._calcsize = _cffi.hypua_c2d_ucs4_calcsize
            self._encode = _cffi.hypua_c2d_ucs4_encode
        elif _UNICODE_SIZE == 2:
            self._calcsize = _cffi.hypua_c2d_ucs2_calcsize
            self._encode = _cffi.hypua_c2d_ucs2_encode
        else:
            raise AssertionError(_UNICODE_SIZE)


if cython_available:
    ComposedJamoEncoder = _cython.ComposedJamoEncoderImplementationOnCython
    DecomposedJamoEncoder = _cython.DecomposedJamoEncoderImplementationOnCython
    DecomposingEncoder = _cython.DecomposingEncoderImplementationOnCython
elif cffi_available:
    ComposedJamoEncoder = ComposedJamoEncoderImplementationOnCFFI
    DecomposedJamoEncoder = DecomposedJamoEncoderImplementationOnCFFI
    DecomposingEncoder = DecomposingEncoderImplementationOnCFFI
else:
    ComposedJamoEncoder = ComposedJamoEncoderImplementationOnPurePython
    DecomposedJamoEncoder = DecomposedJamoEncoderImplementationOnPurePython
    DecomposingEncoder = DecomposingEncoderImplementationOnPurePython
