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
from codecs import IncrementalDecoder
from functools import partial
from struct import Struct
import os.path
import io

from cffi import FFI


_UNICODE_SIZE = array('u').itemsize
try:
    unichr
except NameError:
    # for Python 3
    unichr = chr


class Jamo2PUAIncrementalDecoderCFFIImplementation(IncrementalDecoder):

    def getstate(self):
        state = self._getstate()
        return (b'', state)

    def setstate(self, state):
        self._setstate(state[1])

    def reset(self):
        self._setstate(0)

    def decode(self, jamo_string, final=False):
        jamo_array = array('u', jamo_string)
        jamo_ptr, jamo_len = jamo_array.buffer_info()
        jamo_ptr = self.ffi.cast('void *', jamo_ptr)

        state = self._getstate()
        pua_size = self._calcsize(jamo_ptr, jamo_len)
        self._setstate(state)

        pua_array = array('u', u' ' * pua_size)
        pua_ptr = pua_array.buffer_info()[0]
        pua_ptr = self.ffi.cast('void *', pua_ptr)
        pua_len = self._translate(jamo_ptr, jamo_len, pua_ptr)
        if pua_size != pua_len:
            raise Exception('%r != %r', pua_size, pua_len)

        result = pua_array.tounicode()

        if not final:
            return result

        state = self._getstate()
        pua_size = self._calcsize_flush()
        self._setstate(state)

        if pua_size == 0:
            return result

        pua_array = array('u', u' ' * pua_size)
        pua_ptr = pua_array.buffer_info()[0]
        pua_ptr = self.ffi.cast('void *', pua_ptr)
        pua_len = self._translate(jamo_ptr, jamo_len, pua_ptr)
        if pua_size != pua_len:
            raise Exception('%r != %r', pua_size, pua_len)

        result += pua_array.tounicode()
        return result


class ComposedJamo2PUAIncrementalDecoderCFFIImplementation(
    Jamo2PUAIncrementalDecoderCFFIImplementation
):
    def __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)

        from hypua2jamo._p2j import lib

        if _UNICODE_SIZE == 4:
            _calcsize = \
                lib.hypua_jc2p_translator_u4_calcsize
            _calcsize_flush = \
                lib.hypua_jc2p_translator_u4_calcsize_flush
            _translate = \
                lib.hypua_jc2p_translator_u4_translate
            _translate_flush = \
                lib.hypua_jc2p_translator_u4_translate_flush
        elif _UNICODE_SIZE == 2:
            _calcsize = \
                lib.hypua_jc2p_translator_u2_calcsize
            _calcsize_flush = \
                lib.hypua_jc2p_translator_u2_calcsize_flush
            _translate = \
                lib.hypua_jc2p_translator_u2_translate
            _translate_flush = \
                lib.hypua_jc2p_translator_u2_translate_flush
        else:
            raise Exception(_UNICODE_SIZE)

        self.ffi = ffi = FFI()
        self.lib = lib
        translator_size = lib.hypua_jc2p_translator_size()
        translator_array = array('b', b' ' * translator_size)
        translator_ptr, translator_len = translator_array.buffer_info()
        translator_ptr = ffi.cast('void *', translator_ptr)
        lib.hypua_jc2p_translator_init(translator_ptr)

        self._getstate = partial(
            lib.hypua_jc2p_translator_getstate,
            translator_ptr,
        )
        self._setstate = partial(
            lib.hypua_jc2p_translator_setstate,
            translator_ptr,
        )
        self._calcsize = partial(
            _calcsize, translator_ptr
        )
        self._calcsize_flush = partial(
            _calcsize_flush, translator_ptr
        )
        self._translate = partial(
            _translate, translator_ptr
        )
        self._translate_flush = partial(
            _translate_flush, translator_ptr
        )

        # keep reference to array:
        #       to prevent for translator_ptr to be gc'ed away
        self.__translator = translator_array


class DecomposedJamo2PUAIncrementalDecoderCFFIImplementation(
    Jamo2PUAIncrementalDecoderCFFIImplementation
):
    def __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)

        from hypua2jamo._p2j import lib

        if _UNICODE_SIZE == 4:
            _calcsize = \
                lib.hypua_jd2p_translator_u4_calcsize
            _calcsize_flush = \
                lib.hypua_jd2p_translator_u4_calcsize_flush
            _translate = \
                lib.hypua_jd2p_translator_u4_translate
            _translate_flush = \
                lib.hypua_jd2p_translator_u4_translate_flush
        elif _UNICODE_SIZE == 2:
            _calcsize = \
                lib.hypua_jd2p_translator_u2_calcsize
            _calcsize_flush = \
                lib.hypua_jd2p_translator_u2_calcsize_flush
            _translate = \
                lib.hypua_jd2p_translator_u2_translate
            _translate_flush = \
                lib.hypua_jd2p_translator_u2_translate_flush
        else:
            raise Exception(_UNICODE_SIZE)

        self.ffi = ffi = FFI()
        self.lib = lib
        translator_size = lib.hypua_jd2p_translator_size()
        translator_array = array('b', b' ' * translator_size)
        translator_ptr, translator_len = translator_array.buffer_info()
        translator_ptr = ffi.cast('void *', translator_ptr)
        lib.hypua_jd2p_translator_init(translator_ptr)

        self._getstate = partial(
            lib.hypua_jd2p_translator_getstate,
            translator_ptr,
        )
        self._setstate = partial(
            lib.hypua_jd2p_translator_setstate,
            translator_ptr,
        )
        self._calcsize = partial(
            _calcsize, translator_ptr
        )
        self._calcsize_flush = partial(
            _calcsize_flush, translator_ptr
        )
        self._translate = partial(
            _translate, translator_ptr
        )
        self._translate_flush = partial(
            _translate_flush, translator_ptr
        )

        # keep reference to array:
        #       to prevent for translator_ptr to be gc'ed away
        self.__translator = translator_array


class Node(object):
    '''
    Node of Jamo -> PUA Tree
    '''
    __slots__ = (
        'index',
        'parent_index',
        'jamo_code',
        'pua_code',
        'children',
    )

    def __repr__(self):
        return 'Node(index={}, PUA={})'.format(
            self.index, self.pua_code
        )


class NodeFormatJSON(object):

    def format(self, node):
        return {
            'pua_code': node.pua_code,
            'children': {
                '{:04x}'.format(k): self.format(v)
                for k, v in node.children.items()
            }
        }


_node_struct = Struct('<iHH')


def load_tree_fp(fp):
    root = Node()
    root.index = 0
    root.parent_index = None
    root.jamo_code = None
    root.pua_code = None
    root.children = {}

    index = 1
    nodelist = [root]
    paths = [(None, None)]
    while True:
        data = fp.read(_node_struct.size)
        if len(data) == 0:
            break
        jamo_code, pua_code, parent_id = _node_struct.unpack(data)

        node = Node()
        node.index = index
        node.parent_index = parent_id
        node.jamo_code = jamo_code
        node.pua_code = pua_code
        node.children = {}

        index += 1
        nodelist.append(node)
        paths.append((parent_id, jamo_code))

    for node, (parent_id, jamo_code) in zip(nodelist[1:], paths[1:]):
        if parent_id is None:
            raise Exception()
        if jamo_code is None:
            raise Exception()
        parent = nodelist[parent_id]
        parent.children[jamo_code] = node

    return nodelist


def load_tree(filename):
    filename = os.path.join(
        os.path.dirname(__file__),
        filename,
    )
    with io.open(filename, 'rb') as fp:
        return load_tree_fp(fp)


_jc2p_tree = load_tree('jc2p.bin')
_jd2p_tree = load_tree('jd2p.bin')


class Jamo2PUAIncrementalDecoderPurePythonImplementation(
    IncrementalDecoder
):
    nodelist = None

    def __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)
        self.node = self.nodelist[0]

    def __repr__(self):
        return 'ComposedJamo2PUAIncrementalDecodeUsingPP(node={})'.format(
            self.node
        )

    def getstate(self):
        state = self.node.index
        return (b'', state)

    def setstate(self, state):
        index = state[1]
        self.node = self.nodelist[index]

    def reset(self):
        self.node = self.nodelist[0]

    def decode(self, jamo_string, final=False):
        outbuffer = []
        root = self.nodelist[0]
        src_len = len(jamo_string)
        src_index = 0
        while src_index < src_len:
            jamo_char = jamo_string[src_index]
            jamo_code = ord(jamo_char)
            try:
                node = self.node.children[jamo_code]
            except KeyError:
                #
                # 현재 노드에서 나갈 엣지가 없음
                #

                if self.node.index == 0:
                    outbuffer.append(jamo_char)
                    src_index += 1
                elif self.node.pua_code:
                    outbuffer.append(unichr(self.node.pua_code))
                else:
                    # 노드 업트레이스하며 입력 버퍼 자모 코드 출력
                    for n in _uptrace(self.nodelist, self.node):
                        outbuffer.append(unichr(n.jamo_code))
                    outbuffer.append(jamo_char)

                # 루트 상태로 복귀
                self.node = root
            else:
                # 다음 노드로 이행
                self.node = node
                src_index += 1
        if final:
            # 만약 루트 상태가 아니면
            if self.node.index != 0:
                # 노드 업트레이스하며 입력 버퍼 자모 코드 출력
                for n in _uptrace(self.nodelist, self.node):
                    outbuffer.append(unichr(n.jamo_code))
        return u''.join(outbuffer)


class ComposedJamo2PUAIncrementalDecoderPurePythonImplementation(
    Jamo2PUAIncrementalDecoderPurePythonImplementation
):
    nodelist = _jc2p_tree


class DecomposedJamo2PUAIncrementalDecoderPurePythonImplementation(
    Jamo2PUAIncrementalDecoderPurePythonImplementation
):
    nodelist = _jd2p_tree


def _uptrace(nodelist, node):
    if node.parent_index is None:
        return
    parent = nodelist[node.parent_index]
    for x in _uptrace(nodelist, parent):
        yield x
    yield node


try:
    from hypua2jamo._p2j import lib as _
except ImportError:
    ComposedJamo2PUAIncrementalDecoder =\
        ComposedJamo2PUAIncrementalDecoderPurePythonImplementation
    DecomposedJamo2PUAIncrementalDecoder =\
        DecomposedJamo2PUAIncrementalDecoderPurePythonImplementation
else:
    del _
    ComposedJamo2PUAIncrementalDecoder =\
        ComposedJamo2PUAIncrementalDecoderCFFIImplementation
    DecomposedJamo2PUAIncrementalDecoder =\
        DecomposedJamo2PUAIncrementalDecoderCFFIImplementation
