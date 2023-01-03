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
import io
import platform
import os.path

try:
    from cffi import FFI
    from ._cffi import lib as _cffi
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


class Node(object):
    '''
    Node of Jamo -> PUA Tree
    '''
    __slots__ = (
        'index',
        'parent_index',
        'jamo_char',
        'pua_char',
        'children',
    )

    def __repr__(self):
        return 'Node(index={}, PUA={})'.format(
            self.index, self.pua_char
        )


class NodeFormatJSON(object):

    def format(self, node):
        return {
            'pua_char': node.pua_char,
            'children': {
                '{:04x}'.format(k): self.format(v)
                for k, v in node.children.items()
            }
        }


_node_struct = Struct('<hHH')


def load_tree_fp(fp):
    root = Node()
    root.index = 0
    root.parent_index = None
    root.jamo_char = None
    root.pua_char = None
    root.children = {}

    index = 0
    nodelist = []
    paths = []
    while True:
        data = fp.read(_node_struct.size)
        if len(data) == 0:
            break
        parent_id, jamo_code, pua_code = _node_struct.unpack(data)
        if parent_id == -1:
            parent_id = None
        jamo_char = unichr(jamo_code) if jamo_code else None
        pua_char = unichr(pua_code) if pua_code else None

        node = Node()
        node.index = index
        node.parent_index = parent_id
        node.jamo_char = jamo_char
        node.pua_char = pua_char
        node.children = {}

        index += 1
        nodelist.append(node)
        paths.append((parent_id, jamo_char))

    for node, (parent_id, jamo_char) in zip(nodelist[1:], paths[1:]):
        if parent_id is None:
            raise Exception()
        if jamo_char is None:
            raise Exception()
        parent = nodelist[parent_id]
        parent.children[jamo_char] = node

    return nodelist


def load_tree(filename):
    filename = os.path.join(
        os.path.dirname(__file__),
        filename,
    )
    with io.open(filename, 'rb') as fp:
        return load_tree_fp(fp)


_d2c_tree = load_tree('d2c.bin')
_jc2p_tree = load_tree('jc2p.bin')
_jd2p_tree = load_tree('jd2p.bin')


class BaseDecoderImplementationOnPurePython(
    IncrementalDecoder
):
    nodelist = None

    def __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)
        self.node = self.nodelist[0]

    def __repr__(self):
        return '{}(node={})'.format(
            type(self).__name__,
            self.node,
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
            try:
                node = self.node.children[jamo_char]
            except KeyError:
                #
                # 현재 노드에서 나갈 엣지가 없음
                #

                if self.node.index == 0:
                    # 현 노드가 루트이면 입력 자모 문자를 그대로 출력
                    outbuffer.append(jamo_char)
                    src_index += 1
                elif self.node.pua_char:
                    # 만약 현 노드에 PUA 문자가 매핑되어 있으면
                    # 해당 문자 출력
                    outbuffer.append(self.node.pua_char)
                else:
                    # 현 노드에 PUA 문자가 매핑되어 있지 않으므로
                    # 입력 버퍼 자모열을 출력. 입력 버퍼 자모열은
                    # 노드를 상향 추적하여 얻는다.
                    for n in _uptrace(self.nodelist, self.node):
                        outbuffer.append(n.jamo_char)

                # 루트 상태로 복귀
                self.node = root
            else:
                # 다음 노드로 이행
                self.node = node
                src_index += 1
        if final:
            # 만약 루트 상태가 아니면
            if self.node.index != 0:
                if self.node.pua_char:
                    # 만약 현 노드에 PUA 문자가 매핑되어 있으면
                    # 해당 문자 출력
                    outbuffer.append(self.node.pua_char)
                else:
                    # 현 노드에 PUA 문자가 매핑되어 있지 않으므로
                    # 입력 버퍼 자모열을 출력. 입력 버퍼 자모열은
                    # 노드를 상향 추적하여 얻는다.
                    for n in _uptrace(self.nodelist, self.node):
                        outbuffer.append(n.jamo_char)
        return u''.join(outbuffer)


class PUAComposedDecoder(
    BaseDecoderImplementationOnPurePython
):
    '''
    Composed Jamo-to-PUA decoder

    Pure python implementation.
    '''
    nodelist = _jc2p_tree


PUAComposedDecoderImplementationOnPurePython = PUAComposedDecoder


class PUADecomposedDecoder(
    BaseDecoderImplementationOnPurePython
):
    '''
    Decomposed Jamo-to-PUA decoder

    Pure python implementation.
    '''
    nodelist = _jd2p_tree


PUADecomposedDecoderImplementationOnPurePython = PUADecomposedDecoder


class JamoComposingDecoder(
    BaseDecoderImplementationOnPurePython
):
    '''
    Jamo(decomposed)-to-Jamo(composed) decoder

    Pure python implementation.
    '''
    nodelist = _d2c_tree


JamoComposingDecoderImplementationOnPurePython = JamoComposingDecoder


def _uptrace(nodelist, node):
    '''
    노드를 상향 추적한다.

    현 노드로부터 조상 노드들을 차례로 순회하며 반환한다.
    루트 노드는 제외한다.
    '''

    if node.parent_index is None:
        return
    parent = nodelist[node.parent_index]
    for x in _uptrace(nodelist, parent):
        yield x
    yield node


class BaseDecoderImplementationOnCFFI(IncrementalDecoder):

    def __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)

        if not cffi_available:
            raise NotImplementedError(
                'hypua2jamo._cffi is not available'
            )

        self.ffi = ffi = FFI()
        decoder_alloc_size = _cffi.hypua_decoder_alloc_size()
        decoder_alloc_array = array('b', b' ' * decoder_alloc_size)
        decoder_buf, decoder_buflen = decoder_alloc_array.buffer_info()
        decoder_ptr = ffi.cast('void *', decoder_buf)
        self.init_decoder_c_implementation(decoder_ptr)

        if _UNICODE_SIZE == 4:
            calcsize = _cffi.hypua_decoder_calcsize_ucs4
            decode = _cffi.hypua_decoder_decode_ucs4
            decode_flush = _cffi.hypua_decoder_decode_flush_ucs4
        elif _UNICODE_SIZE == 2:
            calcsize = _cffi.hypua_decoder_calcsize_ucs2
            decode = _cffi.hypua_decoder_decode_ucs2
            decode_flush = _cffi.hypua_decoder_decode_flush_ucs2
        else:
            raise Exception(_UNICODE_SIZE)

        self._getstate = partial(
            _cffi.hypua_decoder_getstate,
            decoder_ptr,
        )
        self._setstate = partial(
            _cffi.hypua_decoder_setstate,
            decoder_ptr,
        )
        self._calcsize = partial(
            calcsize, decoder_ptr
        )
        self._calcsize_flush = partial(
            _cffi.hypua_decoder_calcsize_flush, decoder_ptr
        )
        self._decode = partial(
            decode, decoder_ptr
        )
        self._decode_flush = partial(
            decode_flush, decoder_ptr
        )

        # keep reference to array:
        #       to prevent for decoder_ptr to be gc'ed away
        self.__decoder = decoder_alloc_array

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
        pua_len = self._decode(jamo_ptr, jamo_len, pua_ptr)
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
        pua_len = self._decode_flush(pua_ptr)
        if pua_size != pua_len:
            raise Exception('%r != %r', pua_size, pua_len)

        result += pua_array.tounicode()
        return result


class PUAComposedDecoderImplementationOnCFFI(
    BaseDecoderImplementationOnCFFI
):
    '''
    Composed Jamo-to-PUA decoder

    CFFI implementation.
    '''

    def init_decoder_c_implementation(self, decoder_ptr):
        if not cffi_available:
            raise NotImplementedError(
                'hypua2jamo._cffi is not available'
            )
        _cffi.hypua_decoder_init_jc2p(decoder_ptr)


class PUADecomposedDecoderImplementationOnCFFI(
    BaseDecoderImplementationOnCFFI
):
    '''
    Decomposed Jamo-to-PUA decoder

    CFFI implementation.
    '''
    def init_decoder_c_implementation(self, decoder_ptr):
        if not cffi_available:
            raise NotImplementedError(
                'hypua2jamo._cffi is not available'
            )
        _cffi.hypua_decoder_init_jd2p(decoder_ptr)


class JamoComposingDecoderImplementationOnCFFI(
    BaseDecoderImplementationOnCFFI
):
    '''
    Decomposed Jamo-to-PUA decoder

    CFFI implementation.
    '''
    def init_decoder_c_implementation(self, decoder_ptr):
        if not cffi_available:
            raise NotImplementedError(
                'hypua2jamo._cffi is not available'
            )
        _cffi.hypua_decoder_init_d2c(decoder_ptr)


if cython_available:
    PUAComposedDecoder = _cython.PUAComposedDecoderImplementationOnCython
    PUADecomposedDecoder = _cython.PUADecomposedDecoderImplementationOnCython
    JamoComposingDecoder = _cython.JamoComposingDecoderImplementationOnCython
elif cffi_available:
    PUAComposedDecoder = PUAComposedDecoderImplementationOnCFFI
    PUADecomposedDecoder = PUADecomposedDecoderImplementationOnCFFI
    JamoComposingDecoder = JamoComposingDecoderImplementationOnCFFI
else:
    PUAComposedDecoder = PUAComposedDecoderImplementationOnPurePython
    PUADecomposedDecoder = PUADecomposedDecoderImplementationOnPurePython
    JamoComposingDecoder = JamoComposingDecoderImplementationOnPurePython


# PyPy: Pure Python 구현이 압도적으로 빠르다.
if platform.python_implementation() == 'PyPy':
    PUAComposedDecoder = PUAComposedDecoderImplementationOnPurePython
    PUADecomposedDecoder = PUADecomposedDecoderImplementationOnPurePython
    JamoComposingDecoder = JamoComposingDecoderImplementationOnPurePython
