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
from array import array
from cython import embedsignature
from cpython.mem cimport PyMem_Malloc
from cpython.mem cimport PyMem_Free
from libc.stdlib cimport malloc

cdef extern from *:
    Py_UNICODE* PyUnicode_AsUnicode(object o) except NULL
    Py_ssize_t PyUnicode_GetSize(object o) except -1
    unicode PyUnicode_FromUnicode(Py_UNICODE *u, Py_ssize_t size)

cdef extern from "hypua2jamo.h":
    int hypua_p2jc_ucs4_calcsize(void *src, int srclen);
    int hypua_p2jc_ucs4_encode(void *src, int srclen, void *dst);
    int hypua_p2jc_ucs2_calcsize(void *src, int srclen);
    int hypua_p2jc_ucs2_encode(void *src, int srclen, void *dst);
    int hypua_p2jd_ucs4_calcsize(void *src, int srclen);
    int hypua_p2jd_ucs4_encode(void *src, int srclen, void *dst);
    int hypua_p2jd_ucs2_calcsize(void *src, int srclen);
    int hypua_p2jd_ucs2_encode(void *src, int srclen, void *dst);

    int hypua_jc2p_ucs4_calcsize(void *src, int srclen);
    int hypua_jc2p_ucs4_decode(void *src, int srclen, void *dst);
    int hypua_jc2p_ucs2_calcsize(void *src, int srclen);
    int hypua_jc2p_ucs2_decode(void *src, int srclen, void *dst);
    int hypua_jd2p_ucs4_calcsize(void *src, int srclen);
    int hypua_jd2p_ucs4_decode(void *src, int srclen, void *dst);
    int hypua_jd2p_ucs2_calcsize(void *src, int srclen);
    int hypua_jd2p_ucs2_decode(void *src, int srclen, void *dst);

    int hypua_decoder_alloc_size();
    void hypua_decoder_init_jc2p(void *decoder);
    void hypua_decoder_init_jd2p(void *decoder);
    void hypua_decoder_init(
        void *decoder,
        void *root,
        void *nodelist,
        int nodelistLen
    );
    int hypua_decoder_getstate(void *decoder);
    int hypua_decoder_setstate(void *decoder, int state);
    int hypua_decoder_calcsize_ucs2(void *decoder, void *src, int srclen);
    int hypua_decoder_calcsize_ucs4(void *decoder, void *src, int srclen);
    int hypua_decoder_calcsize_flush(void *decoder);
    int hypua_decoder_decode_ucs2(
        void *decoder,
        void *src,
        int srclen,
        void *dst
    );
    int hypua_decoder_decode_ucs4(
        void *decoder,
        void *src,
        int srclen,
        void *dst
    );
    int hypua_decoder_decode_flush_ucs2(void *decoder, void *dst);
    int hypua_decoder_decode_flush_ucs4(void *decoder, void *dst);


cdef int _UNICODE_SIZE = array('u').itemsize


@embedsignature(True)
cdef class ComposedJamoDecoderImplementationOnCython:
    '''
    Composed Jamo-to-PUA decoder

    Cython implementation.
    '''

    cdef void* _decoder
    cdef int (*_calcsize)(void*, void*, int)
    cdef int (*_calcsize_flush)(void *)
    cdef int (*_decode)(void*, void*, int, void*)
    cdef int (*_decode_flush)(void*, void*)

    def __cinit__(self):
        size = hypua_decoder_alloc_size()
        cdef void *decoder = PyMem_Malloc(size)
        if not decoder:
            raise MemoryError()

        hypua_decoder_init_jc2p(decoder)
        self._decoder = decoder
        if _UNICODE_SIZE == 4:
            self._calcsize = hypua_decoder_calcsize_ucs4
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = hypua_decoder_decode_ucs4
            self._decode_flush = hypua_decoder_decode_flush_ucs4
        elif _UNICODE_SIZE == 2:
            self._calcsize = hypua_decoder_calcsize_ucs2
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = hypua_decoder_decode_ucs2
            self._decode_flush = hypua_decoder_decode_flush_ucs2
        else:
            raise AssertionError(_UNICODE_SIZE)

    def __dealloc__(self):
        PyMem_Free(self._decoder)

    def getstate(self):
        cdef int state = hypua_decoder_getstate(self._decoder)
        return (b'', state)

    def setstate(self, state):
        cdef int stateint = state
        hypua_decoder_setstate(self._decoder, stateint)

    def reset(self):
        hypua_decoder_setstate(self._decoder, 0)

    def decode(self, jamo_string, final=False):
        cdef Py_UNICODE *jamo_buf = PyUnicode_AsUnicode(jamo_string)
        if jamo_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t jamo_len = PyUnicode_GetSize(jamo_string)
        cdef Py_ssize_t state = hypua_decoder_getstate(self._decoder)
        cdef Py_ssize_t pua_len = self._calcsize(
            self._decoder, jamo_buf, jamo_len
        )
        if final:
            pua_len += self._calcsize_flush(self._decoder)

        hypua_decoder_setstate(self._decoder, state)

        cdef Py_UNICODE *pua_buf = <Py_UNICODE *>PyMem_Malloc(pua_len * _UNICODE_SIZE)
        if pua_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t n_translated
        try:
            n_translated = self._decode(
                self._decoder, jamo_buf, jamo_len, pua_buf
            )
            if final:
                n_translated += self._decode_flush(
                    self._decoder, pua_buf + n_translated
                )
            return PyUnicode_FromUnicode(pua_buf, n_translated)
        finally:
            PyMem_Free(pua_buf)


@embedsignature(True)
cdef class DecomposedJamoDecoderImplementationOnCython:
    '''
    Decomposed Jamo-to-PUA decoder

    Cython implementation.
    '''

    cdef void* _decoder
    cdef int (*_calcsize)(void*, void*, int)
    cdef int (*_calcsize_flush)(void *)
    cdef int (*_decode)(void*, void*, int, void*)
    cdef int (*_decode_flush)(void*, void*)

    def __cinit__(self):
        size = hypua_decoder_alloc_size()
        cdef void *decoder = PyMem_Malloc(size)
        if not decoder:
            raise MemoryError()

        hypua_decoder_init_jd2p(decoder)
        self._decoder = decoder
        if _UNICODE_SIZE == 4:
            self._calcsize = hypua_decoder_calcsize_ucs4
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = hypua_decoder_decode_ucs4
            self._decode_flush = hypua_decoder_decode_flush_ucs4
        elif _UNICODE_SIZE == 2:
            self._calcsize = hypua_decoder_calcsize_ucs2
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = hypua_decoder_decode_ucs2
            self._decode_flush = hypua_decoder_decode_flush_ucs2
        else:
            raise AssertionError(_UNICODE_SIZE)

    def __dealloc__(self):
        PyMem_Free(self._decoder)

    def getstate(self):
        cdef int state = hypua_decoder_getstate(self._decoder)
        return (b'', state)

    def setstate(self, state):
        cdef int stateint = state
        hypua_decoder_setstate(self._decoder, stateint)

    def reset(self):
        hypua_decoder_setstate(self._decoder, 0)

    def decode(self, jamo_string, final=False):
        cdef Py_UNICODE *jamo_buf = PyUnicode_AsUnicode(jamo_string)
        if jamo_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t jamo_len = PyUnicode_GetSize(jamo_string)
        cdef Py_ssize_t state = hypua_decoder_getstate(self._decoder)
        cdef Py_ssize_t pua_len = self._calcsize(
            self._decoder, jamo_buf, jamo_len
        )
        if final:
            pua_len += self._calcsize_flush(self._decoder)

        hypua_decoder_setstate(self._decoder, state)

        cdef Py_UNICODE *pua_buf = <Py_UNICODE *>PyMem_Malloc(pua_len * _UNICODE_SIZE)
        if pua_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t n_translated
        try:
            n_translated = self._decode(
                self._decoder, jamo_buf, jamo_len, pua_buf
            )
            if final:
                n_translated += self._decode_flush(
                    self._decoder, pua_buf + n_translated
                )
            return PyUnicode_FromUnicode(pua_buf, n_translated)
        finally:
            PyMem_Free(pua_buf)


@embedsignature(True)
cdef class ComposedJamoEncoderImplementationOnCython:
    '''
    PUA-to-Jamo(composed) encoder

    Cython implementation.
    '''

    cdef int (*_calcsize)(void *src, int srclen);
    cdef int (*_encode)(void *src, int srclen, void *dst);

    def __cinit__(self):
        if _UNICODE_SIZE == 4:
            self._calcsize = hypua_p2jc_ucs4_calcsize
            self._encode = hypua_p2jc_ucs4_encode
        elif _UNICODE_SIZE == 2:
            self._calcsize = hypua_p2jc_ucs2_calcsize
            self._encode = hypua_p2jc_ucs2_encode
        else:
            raise AssertionError(_UNICODE_SIZE)

    def reset(self):
        pass

    def getstate(self):
        return 0

    def setstate(self, state):
        pass

    def encode(self, pua_string, final=False):
        cdef Py_UNICODE *pua_buf = PyUnicode_AsUnicode(pua_string)
        if pua_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t pua_len = PyUnicode_GetSize(pua_string)
        cdef Py_ssize_t jamo_len = self._calcsize(pua_buf, pua_len)
        cdef Py_UNICODE *jamo_buf = <Py_UNICODE *>PyMem_Malloc(jamo_len * _UNICODE_SIZE)
        if jamo_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t n_translated
        try:
            n_translated = self._encode(pua_buf, pua_len, jamo_buf)
            if jamo_len != n_translated:
                raise Exception(
                    'p2jcx translation failed', jamo_len, n_translated
                )
            return PyUnicode_FromUnicode(jamo_buf, n_translated)
        finally:
            PyMem_Free(jamo_buf)


@embedsignature(True)
cdef class DecomposedJamoEncoderImplementationOnCython:
    '''
    PUA-to-Jamo(decomposed) encoder

    Cython implementation.
    '''

    cdef int (*_calcsize)(void *src, int srclen);
    cdef int (*_encode)(void *src, int srclen, void *dst);

    def __cinit__(self):
        if _UNICODE_SIZE == 4:
            self._calcsize = hypua_p2jd_ucs4_calcsize
            self._encode = hypua_p2jd_ucs4_encode
        elif _UNICODE_SIZE == 2:
            self._calcsize = hypua_p2jd_ucs2_calcsize
            self._encode = hypua_p2jd_ucs2_encode
        else:
            raise AssertionError(_UNICODE_SIZE)

    def reset(self):
        pass

    def getstate(self):
        return 0

    def setstate(self, state):
        pass

    def encode(self, pua_string, final=False):
        cdef Py_UNICODE *pua_buf = PyUnicode_AsUnicode(pua_string)
        if pua_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t pua_len = PyUnicode_GetSize(pua_string)
        cdef Py_ssize_t jamo_len = self._calcsize(pua_buf, pua_len)
        cdef Py_UNICODE *jamo_buf = <Py_UNICODE *>PyMem_Malloc(jamo_len * _UNICODE_SIZE)
        if jamo_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t n_translated
        try:
            n_translated = self._encode(pua_buf, pua_len, jamo_buf)
            if jamo_len != n_translated:
                raise Exception(
                    'p2jcx translation failed', jamo_len, n_translated
                )
            return PyUnicode_FromUnicode(jamo_buf, n_translated)
        finally:
            PyMem_Free(jamo_buf)
