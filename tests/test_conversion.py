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

    def test_conversion_c(self):
        # 40 chars
        pua = u'나랏\u302e말\u302f미\u302e 中國귁에\u302e 달아\u302e 문와\u302e로 서르 디\u302e 아니\u302e\u302e'  # noqa

        from cffi import FFI
        from hypua2jamo._p2j import lib

        unicode_size = array('u').itemsize
        if unicode_size == 4:
            translate_calcsize = lib.hypua_p2jc4_translate_calcsize
            translate = lib.hypua_p2jc4_translate
        elif unicode_size == 2:
            translate_calcsize = lib.hypua_p2jc2_translate_calcsize
            translate = lib.hypua_p2jc2_translate
        else:
            raise AssertionError(unicode_size)

        ffi = FFI()

        pua_array = array('u', pua)
        pua_ptr, pua_len = pua_array.buffer_info()
        pua_ptr = ffi.cast('void *', pua_ptr)

        jamo_size = translate_calcsize(pua_ptr, pua_len)
        self.assertEquals(51, jamo_size)
        jamo_array = array('u', u' '*jamo_size)
        jamo_ptr = jamo_array.buffer_info()[0]
        jamo_ptr = ffi.cast('void *', jamo_ptr)
        jamo_len = translate(pua_ptr, pua_len, jamo_ptr)
        self.assertEquals(51, jamo_len)
        jamo = jamo_array.tounicode()

        expected = u'나랏〮말〯ᄊᆞ미〮 中듀ᇰ國귁에〮 달아〮 문ᄍᆞᆼ와〮로 서르 ᄉᆞᄆᆞᆺ디〮 아니〮ᄒᆞᆯᄊᆡ〮'
        self.assertEquals(expected, jamo)
