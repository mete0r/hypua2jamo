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


p2jc_mapping = load_pack('p2jc.bin')
p2jd_mapping = load_pack('p2jd.bin')


def lookup(mapping, pua_code):
    for pua_start, pua_end, jamo_seq_list in mapping:
        if pua_start <= pua_code <= pua_end:
            return jamo_seq_list[pua_code - pua_start]
    return unichr(pua_code)


class PUA2JamoIncrementalEncoderPurePythonImplementation(IncrementalEncoder):

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


class PUA2JamoComposedIncrementalEncoderPurePythonImplementation(
    PUA2JamoIncrementalEncoderPurePythonImplementation
):
    mapping = p2jc_mapping


class PUA2JamoDecomposedIncrementalEncoderPurePythonImplementation(
    PUA2JamoIncrementalEncoderPurePythonImplementation
):
    mapping = p2jd_mapping


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


class PUA2JamoIncrementalEncoderCFFIImplementation(
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
        jamo_len = self._translate(pua_ptr, pua_len, jamo_ptr)
        if jamo_size != jamo_len:
            raise Exception(
                'p2jcx translation failed', jamo_size, jamo_len
            )
        return jamo_array.tounicode()


class PUA2JamoComposedIncrementalEncoderCFFIImplementation(
    PUA2JamoIncrementalEncoderCFFIImplementation
):
    def __init__(self, errors='strict'):
        IncrementalEncoder.__init__(self, errors)

        self._ffi = FFI()

        if _UNICODE_SIZE == 4:
            self._calcsize = _cffi.hypua_p2jc4_translate_calcsize
            self._translate = _cffi.hypua_p2jc4_translate
        elif _UNICODE_SIZE == 2:
            self._calcsize = _cffi.hypua_p2jc2_translate_calcsize
            self._translate = _cffi.hypua_p2jc2_translate
        else:
            raise AssertionError(_UNICODE_SIZE)


class PUA2JamoDecomposedIncrementalEncoderCFFIImplementation(
    PUA2JamoIncrementalEncoderCFFIImplementation
):
    def __init__(self, errors='strict'):
        IncrementalEncoder.__init__(self, errors)

        self._ffi = FFI()

        if _UNICODE_SIZE == 4:
            self._calcsize = _cffi.hypua_p2jd4_translate_calcsize
            self._translate = _cffi.hypua_p2jd4_translate
        elif _UNICODE_SIZE == 2:
            self._calcsize = _cffi.hypua_p2jd2_translate_calcsize
            self._translate = _cffi.hypua_p2jd2_translate
        else:
            raise AssertionError(_UNICODE_SIZE)


if cython_available:
    PUA2JamoComposedIncrementalEncoder =\
        _cython.PUA2JamoComposedIncrementalEncoderCythonImplementation
    PUA2JamoDecomposedIncrementalEncoder =\
        _cython.PUA2JamoDecomposedIncrementalEncoderCythonImplementation
elif cffi_available:
    PUA2JamoComposedIncrementalEncoder =\
        PUA2JamoComposedIncrementalEncoderCFFIImplementation
    PUA2JamoDecomposedIncrementalEncoder =\
        PUA2JamoDecomposedIncrementalEncoderCFFIImplementation
else:
    PUA2JamoComposedIncrementalEncoder =\
        PUA2JamoComposedIncrementalEncoderPurePythonImplementation
    PUA2JamoDecomposedIncrementalEncoder =\
        PUA2JamoDecomposedIncrementalEncoderPurePythonImplementation
