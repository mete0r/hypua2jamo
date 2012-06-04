# -*- coding: utf-8 -*-
from unittest import TestCase

class ConversionTest(TestCase):

    def test_table(self):
        import hypua2jamo.composed
        import hypua2jamo.decomposed
        code = 0xf53a
        expected = u'\u1112\u119e\u11ab'
        self.assertEquals(expected, hypua2jamo.composed.table[code])
        self.assertEquals(expected, hypua2jamo.decomposed.table[code])

    def test_conversion(self):
        pua = u'나랏\u302e말\u302f미\u302e 中國귁에\u302e 달아\u302e 문와\u302e로 서르 디\u302e 아니\u302e\u302e'

        from hypua2jamo import translate
        expected = u'나랏〮말〯ᄊᆞ미〮 中듀ᇰ國귁에〮 달아〮 문ᄍᆞᆼ와〮로 서르 ᄉᆞᄆᆞᆺ디〮 아니〮ᄒᆞᆯᄊᆡ〮'

        result = translate(pua)

        for p, e, r in zip(pua.split(' '), expected.split(' '), result.split(' ')):
            print 'P', p, repr(p)
            print 'E', e, repr(e)
            print 'R', r, repr(r)

        self.assertEquals(expected, result)
