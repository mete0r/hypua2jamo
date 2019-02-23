# -*- coding: utf-8 -*-
from unittest import TestCase
from array import array


class ConversionTest(TestCase):

    def test_table(self):
        from hypua2jamo import get_table
        composed = get_table(True)
        decomposed = get_table(False)

        code = 0xf53a
        expected = u'\u1112\u119e\u11ab'
        self.assertEquals(expected, composed[code])
        self.assertEquals(expected, decomposed[code])

    def test_conversion(self):
        pua = u'나랏\u302e말\u302f미\u302e 中國귁에\u302e 달아\u302e 문와\u302e로 서르 디\u302e 아니\u302e\u302e'  # noqa

        from hypua2jamo import translate
        expected = u'나랏〮말〯ᄊᆞ미〮 中듀ᇰ國귁에〮 달아〮 문ᄍᆞᆼ와〮로 서르 ᄉᆞᄆᆞᆺ디〮 아니〮ᄒᆞᆯᄊᆡ〮'

        result = translate(pua)

        self.assertEquals(expected, result)

    # 40 chars
    pua_string = (
        u'나랏\u302e말\u302f\uebd4미\u302e '
        u'中\ue35f國귁에\u302e 달아\u302e '
        u'문\uf258와\u302e로 '
        u'서르 \ue97d\ue570디\u302e '
        u'아니\u302e\uf53c\uebe1\u302e'
    )
    # 51 chars
    jamo_string = (
        # 0:10 NFC
        u'나랏\u302e말\u302f\u110a\u119e미\u302e '
        # 10:23 not NFC
        u'中\u1103\u1172\u11f0國귁에\u302e 달아\u302e '
        # 23:31 NFC
        u'문\u110d\u119e\u11bc와\u302e로 '
        # 31:42 NFC
        u'서르 \u1109\u119e\u1106\u119e\u11ba디\u302e '
        # 42:51 NFC
        u'아니\u302e\u1112\u119e\u11af\u110a\u11a1\u302e'  # noqa
    )

    def test_p2jcx(self):
        pua = self.pua_string

        from cffi import FFI
        from hypua2jamo._p2j import lib

        unicode_size = array('u').itemsize
        if unicode_size == 4:
            _calcsize = lib.hypua_p2jc4_translate_calcsize
            _translate = lib.hypua_p2jc4_translate
        elif unicode_size == 2:
            _calcsize = lib.hypua_p2jc2_translate_calcsize
            _translate = lib.hypua_p2jc2_translate
        else:
            raise AssertionError(unicode_size)

        ffi = FFI()

        def calcsize(pua_string):
            pua_array = array('u', pua_string)
            pua_ptr, pua_len = pua_array.buffer_info()
            pua_ptr = ffi.cast('void *', pua_ptr)

            jamo_size = _calcsize(pua_ptr, pua_len)
            return jamo_size

        def translate(pua_string):
            pua_array = array('u', pua_string)
            pua_ptr, pua_len = pua_array.buffer_info()
            pua_ptr = ffi.cast('void *', pua_ptr)

            jamo_size = _calcsize(pua_ptr, pua_len)
            jamo_array = array('u', u' '*jamo_size)
            jamo_ptr = jamo_array.buffer_info()[0]
            jamo_ptr = ffi.cast('void *', jamo_ptr)
            jamo_len = _translate(pua_ptr, pua_len, jamo_ptr)
            if jamo_size != jamo_len:
                raise Exception(
                    'p2jcx translation failed', jamo_size, jamo_len
                )
            return jamo_array.tounicode()

        jamo_size = calcsize(pua)
        self.assertEquals(51, jamo_size)

        jamo = translate(pua)
        self.assertEquals(self.jamo_string, jamo)

    def test_jc2px_translate_calcsize(self):
        from cffi import FFI
        from hypua2jamo._p2j import lib

        unicode_size = array('u').itemsize
        if unicode_size == 4:
            _calcsize = lib.hypua_jc2p4_translate_calcsize
        elif unicode_size == 2:
            _calcsize = lib.hypua_jc2p2_translate_calcsize
        else:
            raise AssertionError(unicode_size)

        ffi = FFI()

        def calcsize(jamo_string):
            jamo_array = array('u', jamo_string)
            jamo_ptr, jamo_len = jamo_array.buffer_info()
            jamo_ptr = ffi.cast('void *', jamo_ptr)

            pua_size = _calcsize(jamo_ptr, jamo_len)
            return pua_size

        self.assertEquals(1, calcsize(self.jamo_string[:1]))    # 나
        self.assertEquals(2, calcsize(self.jamo_string[:2]))    # 랏
        self.assertEquals(3, calcsize(self.jamo_string[:3]))
        self.assertEquals(4, calcsize(self.jamo_string[:4]))
        self.assertEquals(5, calcsize(self.jamo_string[:5]))
        self.assertEquals(6, calcsize(self.jamo_string[:6]))
        self.assertEquals(6, calcsize(self.jamo_string[:7]))
        self.assertEquals(7, calcsize(self.jamo_string[:8]))
        self.assertEquals(8, calcsize(self.jamo_string[:9]))
        self.assertEquals(9, calcsize(self.jamo_string[:10]))
        self.assertEquals((
            u'나랏\u302e말\u302f\uebd4미\u302e '
        ), self.pua_string[:9])

        self.assertEquals(10, calcsize(self.jamo_string[:11]))  # 中
        self.assertEquals(11, calcsize(self.jamo_string[:12]))
        self.assertEquals(12, calcsize(self.jamo_string[:13]))
        self.assertEquals(11, calcsize(self.jamo_string[:14]))
        self.assertEquals(12, calcsize(self.jamo_string[:15]))  # 國
        self.assertEquals(13, calcsize(self.jamo_string[:16]))  # 귁
        self.assertEquals(14, calcsize(self.jamo_string[:17]))  # 에
        self.assertEquals(15, calcsize(self.jamo_string[:18]))  # u302e
        self.assertEquals(16, calcsize(self.jamo_string[:19]))  # u0020

        self.assertEquals(17, calcsize(self.jamo_string[:20]))  # 달
        self.assertEquals(18, calcsize(self.jamo_string[:21]))  # 아
        self.assertEquals(19, calcsize(self.jamo_string[:22]))  # u302e
        self.assertEquals(20, calcsize(self.jamo_string[:23]))  # u0020
        self.assertEquals((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
        ), self.pua_string[:20])

        self.assertEquals(21, calcsize(self.jamo_string[:24]))  # 문
        self.assertEquals(22, calcsize(self.jamo_string[:25]))  #
        self.assertEquals(22, calcsize(self.jamo_string[:26]))  #
        self.assertEquals(22, calcsize(self.jamo_string[:27]))  #
        self.assertEquals(23, calcsize(self.jamo_string[:28]))  # 와
        self.assertEquals(24, calcsize(self.jamo_string[:29]))  # u302e
        self.assertEquals(25, calcsize(self.jamo_string[:30]))  # 로
        self.assertEquals(26, calcsize(self.jamo_string[:31]))  # u0020
        self.assertEquals((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
        ), self.pua_string[:26])

        self.assertEquals(27, calcsize(self.jamo_string[:32]))  # 서
        self.assertEquals(28, calcsize(self.jamo_string[:33]))  # 르
        self.assertEquals(29, calcsize(self.jamo_string[:34]))  # u0020
        self.assertEquals((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
            u'서르 '
        ), self.pua_string[:29])

        self.assertEquals(30, calcsize(self.jamo_string[:35]))
        self.assertEquals(30, calcsize(self.jamo_string[:36]))
        self.assertEquals(31, calcsize(self.jamo_string[:37]))
        self.assertEquals(31, calcsize(self.jamo_string[:38]))
        self.assertEquals(31, calcsize(self.jamo_string[:39]))
        self.assertEquals(32, calcsize(self.jamo_string[:40]))  # 디
        self.assertEquals(33, calcsize(self.jamo_string[:41]))  # u302e
        self.assertEquals(34, calcsize(self.jamo_string[:42]))  # u0020
        self.assertEquals((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
            u'서르 \ue97d\ue570디\u302e '
        ), self.pua_string[:34])

        self.assertEquals(35, calcsize(self.jamo_string[:43]))  # 아
        self.assertEquals(36, calcsize(self.jamo_string[:44]))  # 니
        self.assertEquals(37, calcsize(self.jamo_string[:45]))  # u302e
        self.assertEquals(38, calcsize(self.jamo_string[:46]))
        self.assertEquals(38, calcsize(self.jamo_string[:47]))
        self.assertEquals(38, calcsize(self.jamo_string[:48]))
        self.assertEquals(39, calcsize(self.jamo_string[:49]))
        self.assertEquals(39, calcsize(self.jamo_string[:50]))
        self.assertEquals(40, calcsize(self.jamo_string[:51]))  # 302e
        self.assertEquals((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
            u'서르 \ue97d\ue570디\u302e '
            u'아니\u302e\uf53c\uebe1\u302e'
        ), self.pua_string[:40])

        self.assertEquals(40, calcsize(self.jamo_string))

    def test_jc2px_translate(self):
        from cffi import FFI
        from hypua2jamo._p2j import lib

        unicode_size = array('u').itemsize
        if unicode_size == 4:
            _translate = lib.hypua_jc2p4_translate
            _calcsize = lib.hypua_jc2p4_translate_calcsize
        elif unicode_size == 2:
            _translate = lib.hypua_jc2p2_translate
            _calcsize = lib.hypua_jc2p2_translate_calcsize
        else:
            raise AssertionError(unicode_size)

        ffi = FFI()

        def translate(jamo_string):
            jamo_array = array('u', jamo_string)
            jamo_ptr, jamo_len = jamo_array.buffer_info()
            jamo_ptr = ffi.cast('void *', jamo_ptr)

            pua_size = _calcsize(jamo_ptr, jamo_len)

            pua_array = array('u', u' ' * pua_size)
            pua_ptr = pua_array.buffer_info()[0]
            pua_ptr = ffi.cast('void *', pua_ptr)
            pua_len = _translate(jamo_ptr, jamo_len, pua_ptr)
            if pua_size != pua_len:
                raise Exception('%r != %r', pua_size, pua_len)
            return pua_array.tounicode()

        pua = self.pua_string
        jamo = self.jamo_string

        self.assertEquals(pua[:1], translate(jamo[:1]))    # 나
        self.assertEquals(pua[:2], translate(jamo[:2]))    # 랏
        self.assertEquals(pua[:3], translate(jamo[:3]))
        self.assertEquals(pua[:4], translate(jamo[:4]))
        self.assertEquals(pua[:5], translate(jamo[:5]))
        self.assertEquals(pua[:5] + u'\uf7ca', translate(jamo[:6]))
        self.assertEquals(pua[:6], translate(jamo[:7]))
        self.assertEquals(pua[:7], translate(jamo[:8]))
        self.assertEquals(pua[:8], translate(jamo[:9]))
        self.assertEquals(pua[:9], translate(jamo[:10]))

        self.assertEquals(pua[:10], translate(jamo[:11]))  # 中
        self.assertEquals(pua[:10] + u'\uf790', translate(jamo[:12]))
        self.assertEquals(pua[:10] + u'\u1103\u1172', translate(jamo[:13]))
        self.assertEquals(pua[:11], translate(jamo[:14]))
        self.assertEquals(pua[:12], translate(jamo[:15]))  # 國
        self.assertEquals(pua[:13], translate(jamo[:16]))  # 귁
        self.assertEquals(pua[:14], translate(jamo[:17]))  # 에
        self.assertEquals(pua[:15], translate(jamo[:18]))  # u302e
        self.assertEquals(pua[:16], translate(jamo[:19]))  # u0020

        self.assertEquals(pua[:17], translate(jamo[:20]))  # 달
        self.assertEquals(pua[:18], translate(jamo[:21]))  # 아
        self.assertEquals(pua[:19], translate(jamo[:22]))  # u302e
        self.assertEquals(pua[:20], translate(jamo[:23]))  # u0020

        self.assertEquals(pua[:21], translate(jamo[:24]))  # 문
        self.assertEquals(pua[:21] + u'\uf7ea', translate(jamo[:25]))  #
        self.assertEquals(pua[:21] + u'\uf250', translate(jamo[:26]))  #
        self.assertEquals(pua[:22], translate(jamo[:27]))  #
        self.assertEquals(pua[:23], translate(jamo[:28]))  # 와
        self.assertEquals(pua[:24], translate(jamo[:29]))  # u302e
        self.assertEquals(pua[:25], translate(jamo[:30]))  # 로
        self.assertEquals(pua[:26], translate(jamo[:31]))  # u0020

        self.assertEquals(pua[:27], translate(jamo[:32]))  # 서
        self.assertEquals(pua[:28], translate(jamo[:33]))  # 르
        self.assertEquals(pua[:29], translate(jamo[:34]))  # u0020

        self.assertEquals(pua[:29] + u'\uf7c2', translate(jamo[:35]))
        self.assertEquals(pua[:30], translate(jamo[:36]))
        self.assertEquals(pua[:30] + u'\uf7a8', translate(jamo[:37]))
        self.assertEquals(pua[:30] + u'\ue560', translate(jamo[:38]))
        self.assertEquals(pua[:31], translate(jamo[:39]))
        self.assertEquals(pua[:32], translate(jamo[:40]))  # 디
        self.assertEquals(pua[:33], translate(jamo[:41]))  # u302e
        self.assertEquals(pua[:34], translate(jamo[:42]))  # u0020

        self.assertEquals(pua[:35], translate(jamo[:43]))  # 아
        self.assertEquals(pua[:36], translate(jamo[:44]))  # 니
        self.assertEquals(pua[:37], translate(jamo[:45]))  # u302e
        self.assertEquals(pua[:37] + u'\uf7fc', translate(jamo[:46]))
        self.assertEquals(pua[:37] + u'\uf537', translate(jamo[:47]))
        self.assertEquals(pua[:38], translate(jamo[:48]))
        self.assertEquals(pua[:38] + u'\uf7ca', translate(jamo[:49]))
        self.assertEquals(pua[:39], translate(jamo[:50]))
        self.assertEquals(pua[:40], translate(jamo[:51]))  # 302e

        self.assertEquals(pua[:40], translate(jamo))

    def test_jc2px_decoder(self):
        from codecs import IncrementalDecoder
        from cffi import FFI

        class ComposedJamo2PUAIncrementalDecoder(IncrementalDecoder):
            def __init__(self, errors='strict'):
                IncrementalDecoder.__init__(self, errors)

                from hypua2jamo._p2j import lib

                unicode_size = array('u').itemsize
                if unicode_size == 4:
                    _calcsize = \
                        lib.hypua_jc2p_translator_u4_calcsize
                    _calcsize_flush = \
                        lib.hypua_jc2p_translator_u4_calcsize_flush
                    _translate = \
                        lib.hypua_jc2p_translator_u4_translate
                    _translate_flush = \
                        lib.hypua_jc2p_translator_u4_translate_flush
                elif unicode_size == 2:
                    _calcsize = \
                        lib.hypua_jc2p_translator_u2_calcsize
                    _calcsize_flush = \
                        lib.hypua_jc2p_translator_u2_calcsize_flush
                    _translate = \
                        lib.hypua_jc2p_translator_u2_translate
                    _translate_flush = \
                        lib.hypua_jc2p_translator_u2_translate_flush
                else:
                    raise Exception(unicode_size)

                self.ffi = ffi = FFI()
                self.lib = lib
                translator_size = lib.hypua_jc2p_translator_size()
                translator_array = array('b', b' ' * translator_size)
                translator_ptr, translator_len = translator_array.buffer_info()
                translator_ptr = ffi.cast('void *', translator_ptr)
                lib.hypua_jc2p_translator_init(translator_ptr)

                from functools import partial
                self.__getstate = partial(
                    lib.hypua_jc2p_translator_getstate,
                    translator_ptr,
                )
                self.__setstate = partial(
                    lib.hypua_jc2p_translator_setstate,
                    translator_ptr,
                )
                self.__calcsize = partial(
                    _calcsize, translator_ptr
                )
                self.__calcsize_flush = partial(
                    _calcsize_flush, translator_ptr
                )
                self.__translate = partial(
                    _translate, translator_ptr
                )
                self.__translate_flush = partial(
                    _translate_flush, translator_ptr
                )

                # keep reference to array:
                #       to prevent for translator_ptr to be gc'ed away
                self.__translator = translator_array

            def getstate(self):
                state = self.__getstate()
                return (b'', state)

            def setstate(self, state):
                self.__setstate(state[1])

            def reset(self):
                self.__setstate(0)

            def decode(self, jamo_string, final=False):
                jamo_array = array('u', jamo_string)
                jamo_ptr, jamo_len = jamo_array.buffer_info()
                jamo_ptr = self.ffi.cast('void *', jamo_ptr)

                state = self.__getstate()
                pua_size = self.__calcsize(jamo_ptr, jamo_len)
                self.__setstate(state)

                pua_array = array('u', u' ' * pua_size)
                pua_ptr = pua_array.buffer_info()[0]
                pua_ptr = self.ffi.cast('void *', pua_ptr)
                pua_len = self.__translate(jamo_ptr, jamo_len, pua_ptr)
                if pua_size != pua_len:
                    raise Exception('%r != %r', pua_size, pua_len)

                result = pua_array.tounicode()

                if not final:
                    return result

                state = self.__getstate()
                pua_size = self.__calcsize_flush()
                self.__setstate(state)

                if pua_size == 0:
                    return result

                pua_array = array('u', u' ' * pua_size)
                pua_ptr = pua_array.buffer_info()[0]
                pua_ptr = self.ffi.cast('void *', pua_ptr)
                pua_len = self.__translate(jamo_ptr, jamo_len, pua_ptr)
                if pua_size != pua_len:
                    raise Exception('%r != %r', pua_size, pua_len)

                result += pua_array.tounicode()
                return result

        decoder = ComposedJamo2PUAIncrementalDecoder()
        self.assertEquals((b'', 0), decoder.getstate())

        for chunk_size in range(1, 1 + len(self.jamo_string)):
            decoder.reset()

            jamo_string = self.jamo_string
            pua = u''

            while chunk_size <= len(jamo_string):
                pua += decoder.decode(jamo_string[:chunk_size], False)
                jamo_string = jamo_string[chunk_size:]
            pua += decoder.decode(jamo_string, True)
            self.assertEquals(self.pua_string, pua)
