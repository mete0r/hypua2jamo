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
from cpython.mem cimport PyMem_Malloc
from cpython.mem cimport PyMem_Free
from libc.stdlib cimport malloc

cdef extern from *:
    Py_UNICODE* PyUnicode_AsUnicode(object o) except NULL
    Py_ssize_t PyUnicode_GetSize(object o) except -1
    unicode PyUnicode_FromUnicode(Py_UNICODE *u, Py_ssize_t size)

cdef extern from "hypua2jamo.h":
    int hypua_p2jc4_translate_calcsize(void *src, int srclen);
    int hypua_p2jc4_translate(void *src, int srclen, void *dst);
    int hypua_p2jd4_translate_calcsize(void *src, int srclen);
    int hypua_p2jd4_translate(void *src, int srclen, void *dst);
    int hypua_p2jc2_translate_calcsize(void *src, int srclen);
    int hypua_p2jc2_translate(void *src, int srclen, void *dst);
    int hypua_p2jd2_translate_calcsize(void *src, int srclen);
    int hypua_p2jd2_translate(void *src, int srclen, void *dst);

    int hypua_jc2p4_translate_calcsize(void *src, int srclen);
    int hypua_jc2p4_translate(void *src, int srclen, void *dst);
    int hypua_jc2p2_translate_calcsize(void *src, int srclen);
    int hypua_jc2p2_translate(void *src, int srclen, void *dst);
    int hypua_jd2p4_translate_calcsize(void *src, int srclen);
    int hypua_jd2p4_translate(void *src, int srclen, void *dst);
    int hypua_jd2p2_translate_calcsize(void *src, int srclen);
    int hypua_jd2p2_translate(void *src, int srclen, void *dst);

    int hypua_jc2p_translator_size();
    int hypua_jc2p_translator_init(void *);
    int hypua_jc2p_translator_getstate(void *);
    int hypua_jc2p_translator_setstate(void *, int);
    int hypua_jc2p_translator_u2_calcsize(void *, void *src, int srclen);
    int hypua_jc2p_translator_u2_calcsize_flush(void *);
    int hypua_jc2p_translator_u2_translate(void *, void *src, int srclen, void *dst);
    int hypua_jc2p_translator_u2_translate_flush(void *, void *dst);
    int hypua_jc2p_translator_u4_calcsize(void *, void *src, int srclen);
    int hypua_jc2p_translator_u4_calcsize_flush(void *);
    int hypua_jc2p_translator_u4_translate(void *, void *src, int srclen, void *dst);
    int hypua_jc2p_translator_u4_translate_flush(void *, void *dst);

    int hypua_jd2p_translator_size();
    int hypua_jd2p_translator_init(void *);
    int hypua_jd2p_translator_getstate(void *);
    int hypua_jd2p_translator_setstate(void *, int);
    int hypua_jd2p_translator_u2_calcsize(void *, void *src, int srclen);
    int hypua_jd2p_translator_u2_calcsize_flush(void *);
    int hypua_jd2p_translator_u2_translate(void *, void *src, int srclen, void *dst);
    int hypua_jd2p_translator_u2_translate_flush(void *, void *dst);
    int hypua_jd2p_translator_u4_calcsize(void *, void *src, int srclen);
    int hypua_jd2p_translator_u4_calcsize_flush(void *);
    int hypua_jd2p_translator_u4_translate(void *, void *src, int srclen, void *dst);
    int hypua_jd2p_translator_u4_translate_flush(void *, void *dst);


cdef int _UNICODE_SIZE = array('u').itemsize


cdef class ComposedJamo2PUAIncrementalDecoderCythonImplementation:

    cdef void* _translator
    cdef int (*_calcsize)(void*, void*, int)
    cdef int (*_calcsize_flush)(void *)
    cdef int (*_translate)(void*, void*, int, void*)
    cdef int (*_translate_flush)(void*, void*)

    def __cinit__(self):
        size = hypua_jc2p_translator_size()
        cdef void *translator = PyMem_Malloc(size)
        if not translator:
            raise MemoryError()

        hypua_jc2p_translator_init(translator)
        self._translator = translator
        if _UNICODE_SIZE == 4:
            self._calcsize = hypua_jc2p_translator_u4_calcsize
            self._calcsize_flush = hypua_jc2p_translator_u4_calcsize_flush
            self._translate = hypua_jc2p_translator_u4_translate
            self._translate_flush = hypua_jc2p_translator_u4_translate_flush
        elif _UNICODE_SIZE == 2:
            self._calcsize = hypua_jc2p_translator_u2_calcsize
            self._calcsize_flush = hypua_jc2p_translator_u2_calcsize_flush
            self._translate = hypua_jc2p_translator_u2_translate
            self._translate_flush = hypua_jc2p_translator_u2_translate_flush
        else:
            raise AssertionError(_UNICODE_SIZE)

    def __dealloc__(self):
        PyMem_Free(self._translator)

    def getstate(self):
        cdef int state = hypua_jc2p_translator_getstate(self._translator)
        return (b'', state)

    def setstate(self, state):
        cdef int stateint = state
        hypua_jc2p_translator_setstate(self._translator, stateint)

    def reset(self):
        hypua_jc2p_translator_setstate(self._translator, 0)

    def decode(self, jamo_string, final=False):
        cdef Py_UNICODE *jamo_buf = PyUnicode_AsUnicode(jamo_string)
        if jamo_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t jamo_len = PyUnicode_GetSize(jamo_string)
        cdef Py_ssize_t state = hypua_jc2p_translator_getstate(self._translator)
        cdef Py_ssize_t pua_len = self._calcsize(
            self._translator, jamo_buf, jamo_len
        )
        if final:
            pua_len += self._calcsize_flush(self._translator)

        hypua_jc2p_translator_setstate(self._translator, state)

        cdef Py_UNICODE *pua_buf = <Py_UNICODE *>PyMem_Malloc(pua_len * _UNICODE_SIZE)
        if pua_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t n_translated
        try:
            n_translated = self._translate(
                self._translator, jamo_buf, jamo_len, pua_buf
            )
            if final:
                n_translated += self._translate_flush(
                    self._translator, pua_buf + n_translated
                )
            return PyUnicode_FromUnicode(pua_buf, n_translated)
        finally:
            PyMem_Free(pua_buf)


cdef class DecomposedJamo2PUAIncrementalDecoderCythonImplementation:

    cdef void* _translator
    cdef int (*_calcsize)(void*, void*, int)
    cdef int (*_calcsize_flush)(void *)
    cdef int (*_translate)(void*, void*, int, void*)
    cdef int (*_translate_flush)(void*, void*)

    def __cinit__(self):
        size = hypua_jd2p_translator_size()
        cdef void *translator = PyMem_Malloc(size)
        if not translator:
            raise MemoryError()

        hypua_jd2p_translator_init(translator)
        self._translator = translator
        if _UNICODE_SIZE == 4:
            self._calcsize = hypua_jd2p_translator_u4_calcsize
            self._calcsize_flush = hypua_jd2p_translator_u4_calcsize_flush
            self._translate = hypua_jd2p_translator_u4_translate
            self._translate_flush = hypua_jd2p_translator_u4_translate_flush
        elif _UNICODE_SIZE == 2:
            self._calcsize = hypua_jd2p_translator_u2_calcsize
            self._calcsize_flush = hypua_jd2p_translator_u2_calcsize_flush
            self._translate = hypua_jd2p_translator_u2_translate
            self._translate_flush = hypua_jd2p_translator_u2_translate_flush
        else:
            raise AssertionError(_UNICODE_SIZE)

    def __dealloc__(self):
        PyMem_Free(self._translator)

    def getstate(self):
        cdef int state = hypua_jd2p_translator_getstate(self._translator)
        return (b'', state)

    def setstate(self, state):
        cdef int stateint = state
        hypua_jd2p_translator_setstate(self._translator, stateint)

    def reset(self):
        hypua_jd2p_translator_setstate(self._translator, 0)

    def decode(self, jamo_string, final=False):
        cdef Py_UNICODE *jamo_buf = PyUnicode_AsUnicode(jamo_string)
        if jamo_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t jamo_len = PyUnicode_GetSize(jamo_string)
        cdef Py_ssize_t state = hypua_jd2p_translator_getstate(self._translator)
        cdef Py_ssize_t pua_len = self._calcsize(
            self._translator, jamo_buf, jamo_len
        )
        if final:
            pua_len += self._calcsize_flush(self._translator)

        hypua_jd2p_translator_setstate(self._translator, state)

        cdef Py_UNICODE *pua_buf = <Py_UNICODE *>PyMem_Malloc(pua_len * _UNICODE_SIZE)
        if pua_buf is NULL:
            raise MemoryError()
        cdef Py_ssize_t n_translated
        try:
            n_translated = self._translate(
                self._translator, jamo_buf, jamo_len, pua_buf
            )
            if final:
                n_translated += self._translate_flush(
                    self._translator, pua_buf + n_translated
                )
            return PyUnicode_FromUnicode(pua_buf, n_translated)
        finally:
            PyMem_Free(pua_buf)


cdef class PUA2JamoComposedIncrementalEncoderCythonImplementation:

    cdef int (*_calcsize)(void *src, int srclen);
    cdef int (*_translate)(void *src, int srclen, void *dst);

    def __cinit__(self):
        if _UNICODE_SIZE == 4:
            self._calcsize = hypua_p2jc4_translate_calcsize
            self._translate = hypua_p2jc4_translate
        elif _UNICODE_SIZE == 2:
            self._calcsize = hypua_p2jc2_translate_calcsize
            self._translate = hypua_p2jc2_translate
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
            n_translated = self._translate(pua_buf, pua_len, jamo_buf)
            if jamo_len != n_translated:
                raise Exception(
                    'p2jcx translation failed', jamo_len, n_translated
                )
            return PyUnicode_FromUnicode(jamo_buf, n_translated)
        finally:
            PyMem_Free(jamo_buf)


cdef class PUA2JamoDecomposedIncrementalEncoderCythonImplementation:

    cdef int (*_calcsize)(void *src, int srclen);
    cdef int (*_translate)(void *src, int srclen, void *dst);

    def __cinit__(self):
        if _UNICODE_SIZE == 4:
            self._calcsize = hypua_p2jd4_translate_calcsize
            self._translate = hypua_p2jd4_translate
        elif _UNICODE_SIZE == 2:
            self._calcsize = hypua_p2jd2_translate_calcsize
            self._translate = hypua_p2jd2_translate
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
            n_translated = self._translate(pua_buf, pua_len, jamo_buf)
            if jamo_len != n_translated:
                raise Exception(
                    'p2jcx translation failed', jamo_len, n_translated
                )
            return PyUnicode_FromUnicode(jamo_buf, n_translated)
        finally:
            PyMem_Free(jamo_buf)
