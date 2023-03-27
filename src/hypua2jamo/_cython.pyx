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

cdef extern from *:
    Py_UNICODE* PyUnicode_AsUnicode(object o) except NULL
    Py_ssize_t PyUnicode_GetSize(object o) except -1
    unicode PyUnicode_FromUnicode(Py_UNICODE *u, Py_ssize_t size)

cdef extern from "hypua2jamo.h":
    ctypedef unsigned short uint16_t
    ctypedef unsigned int uint32_t
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


cdef int _UNICODE_SIZE = array('u').itemsize

ctypedef size_t (*_decoder_calcsize_fn)(void*, void*, size_t)
ctypedef size_t (*_decoder_decode_fn)(void*, void*, size_t, void*)


cdef class JamoDecoderImplementationOnCython:

    cdef void* _decoder
    cdef _decoder_calcsize_fn _calcsize
    cdef size_t (*_calcsize_flush)(void *)
    cdef _decoder_decode_fn _decode
    cdef size_t (*_decode_flush)(void*, void*)

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
cdef class PUAComposedDecoderImplementationOnCython(
    JamoDecoderImplementationOnCython
):
    '''
    Composed Jamo-to-PUA decoder

    Cython implementation.
    '''

    def __cinit__(self):
        size = hypua_decoder_alloc_size()
        cdef void *decoder = PyMem_Malloc(size)
        if not decoder:
            raise MemoryError()

        hypua_decoder_init_jc2p(decoder)
        self._decoder = decoder
        if _UNICODE_SIZE == 4:
            self._calcsize = <_decoder_calcsize_fn>hypua_decoder_calcsize_ucs4
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = <_decoder_decode_fn>hypua_decoder_decode_ucs4
            self._decode_flush = hypua_decoder_decode_flush_ucs4
        elif _UNICODE_SIZE == 2:
            self._calcsize = <_decoder_calcsize_fn>hypua_decoder_calcsize_ucs2
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = <_decoder_decode_fn>hypua_decoder_decode_ucs2
            self._decode_flush = hypua_decoder_decode_flush_ucs2
        else:
            raise AssertionError(_UNICODE_SIZE)


@embedsignature(True)
cdef class PUADecomposedDecoderImplementationOnCython(
    JamoDecoderImplementationOnCython
):
    '''
    Decomposed Jamo-to-PUA decoder

    Cython implementation.
    '''

    def __cinit__(self):
        size = hypua_decoder_alloc_size()
        cdef void *decoder = PyMem_Malloc(size)
        if not decoder:
            raise MemoryError()

        hypua_decoder_init_jd2p(decoder)
        self._decoder = decoder
        if _UNICODE_SIZE == 4:
            self._calcsize = <_decoder_calcsize_fn>hypua_decoder_calcsize_ucs4
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = <_decoder_decode_fn>hypua_decoder_decode_ucs4
            self._decode_flush = hypua_decoder_decode_flush_ucs4
        elif _UNICODE_SIZE == 2:
            self._calcsize = <_decoder_calcsize_fn>hypua_decoder_calcsize_ucs2
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = <_decoder_decode_fn>hypua_decoder_decode_ucs2
            self._decode_flush = hypua_decoder_decode_flush_ucs2
        else:
            raise AssertionError(_UNICODE_SIZE)


@embedsignature(True)
cdef class JamoComposingDecoderImplementationOnCython(
    JamoDecoderImplementationOnCython
):
    '''
    Jamo(decomposed)-to-Jamo(composing) decoder

    Cython implementation.
    '''

    def __cinit__(self):
        size = hypua_decoder_alloc_size()
        cdef void *decoder = PyMem_Malloc(size)
        if not decoder:
            raise MemoryError()

        hypua_decoder_init_d2c(decoder)

        self._decoder = decoder
        if _UNICODE_SIZE == 4:
            self._calcsize = <_decoder_calcsize_fn>hypua_decoder_calcsize_ucs4
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = <_decoder_decode_fn>hypua_decoder_decode_ucs4
            self._decode_flush = hypua_decoder_decode_flush_ucs4
        elif _UNICODE_SIZE == 2:
            self._calcsize = <_decoder_calcsize_fn>hypua_decoder_calcsize_ucs2
            self._calcsize_flush = hypua_decoder_calcsize_flush
            self._decode = <_decoder_decode_fn>hypua_decoder_decode_ucs2
            self._decode_flush = hypua_decoder_decode_flush_ucs2
        else:
            raise AssertionError(_UNICODE_SIZE)

ctypedef size_t (*_encoder_calcsize_fn)(void*, size_t)
ctypedef size_t (*_encoder_encode_fn)(void *, size_t, void *)


cdef class JamoEncoderImplementationOnCython:
    '''
    PUA-to-Jamo(composed) encoder

    Cython implementation.
    '''

    cdef _encoder_calcsize_fn _calcsize
    cdef _encoder_encode_fn _encode

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
cdef class PUAComposedEncoderImplementationOnCython(
    JamoEncoderImplementationOnCython
):
    '''
    PUA-to-Jamo(composed) encoder

    Cython implementation.
    '''

    def __cinit__(self):
        if _UNICODE_SIZE == 4:
            self._calcsize = <_encoder_calcsize_fn>hypua_p2jc_ucs4_calcsize
            self._encode = <_encoder_encode_fn>hypua_p2jc_ucs4_encode
        elif _UNICODE_SIZE == 2:
            self._calcsize = <_encoder_calcsize_fn>hypua_p2jc_ucs2_calcsize
            self._encode = <_encoder_encode_fn>hypua_p2jc_ucs2_encode
        else:
            raise AssertionError(_UNICODE_SIZE)


@embedsignature(True)
cdef class PUADecomposedEncoderImplementationOnCython(
    JamoEncoderImplementationOnCython
):
    '''
    PUA-to-Jamo(decomposed) encoder

    Cython implementation.
    '''

    def __cinit__(self):
        if _UNICODE_SIZE == 4:
            self._calcsize = <_encoder_calcsize_fn>hypua_p2jd_ucs4_calcsize
            self._encode = <_encoder_encode_fn>hypua_p2jd_ucs4_encode
        elif _UNICODE_SIZE == 2:
            self._calcsize = <_encoder_calcsize_fn>hypua_p2jd_ucs2_calcsize
            self._encode = <_encoder_encode_fn>hypua_p2jd_ucs2_encode
        else:
            raise AssertionError(_UNICODE_SIZE)


@embedsignature(True)
cdef class JamoDecomposingEncoderImplementationOnCython(
    JamoEncoderImplementationOnCython
):
    '''
    Jamo(composed)-to-Jamo(decomposed) encoder

    Cython implementation.
    '''

    def __cinit__(self):
        if _UNICODE_SIZE == 4:
            self._calcsize = <_encoder_calcsize_fn>hypua_c2d_ucs4_calcsize
            self._encode = <_encoder_encode_fn>hypua_c2d_ucs4_encode
        elif _UNICODE_SIZE == 2:
            self._calcsize = <_encoder_calcsize_fn>hypua_c2d_ucs2_calcsize
            self._encode = <_encoder_encode_fn>hypua_c2d_ucs2_encode
        else:
            raise AssertionError(_UNICODE_SIZE)
