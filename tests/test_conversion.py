# -*- coding: utf-8 -*-
from unittest import TestCase
from array import array


class Fixtures(object):

    class HunMinPreface(object):
        # 40 chars
        pua_string = (
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
            u'서르 \ue97d\ue570디\u302e '
            u'아니\u302e\uf53c\uebe1\u302e'
        )

        # 51 chars
        composed_jamo_string = (
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

        # 55 chars
        decomposed_jamo_string = (
            u'나랏\u302e말\u302f\u1109\u1109\u119e미\u302e '
            u'中\u1103\u1172\u11f0國귁에\u302e 달아\u302e '
            u'문\u110c\u110c\u119e\u11bc와\u302e로 '
            u'서르 \u1109\u119e\u1106\u119e\u11ba디\u302e '
            u'아니\u302e\u1112\u119e\u11af\u1109\u1109\u119e\u1175\u302e'  # noqa
        )


class TranslateTest(TestCase):

    def test_translate(self):
        pua = u'나랏\u302e말\u302f미\u302e 中國귁에\u302e 달아\u302e 문와\u302e로 서르 디\u302e 아니\u302e\u302e'  # noqa

        from hypua2jamo import translate
        expected = u'나랏〮말〯ᄊᆞ미〮 中듀ᇰ國귁에〮 달아〮 문ᄍᆞᆼ와〮로 서르 ᄉᆞᄆᆞᆺ디〮 아니〮ᄒᆞᆯᄊᆡ〮'

        result = translate(pua)

        self.assertEquals(expected, result)

    def test_translate_composed(self):
        from hypua2jamo import translate

        jamo_string = translate(
            Fixtures.HunMinPreface.pua_string,
        )
        self.assertEquals(
            Fixtures.HunMinPreface.composed_jamo_string,
            jamo_string,
        )

    def test_translate_decomposed(self):
        from hypua2jamo import translate

        jamo_string = translate(
            Fixtures.HunMinPreface.pua_string,
            composed=False
        )
        self.assertEquals(
            Fixtures.HunMinPreface.decomposed_jamo_string,
            jamo_string,
        )


class CFFITest(TestCase):

    pua_string = Fixtures.HunMinPreface.pua_string
    jamo_string = Fixtures.HunMinPreface.composed_jamo_string

    def test_jc2p_calcsize(self):
        from cffi import FFI
        from hypua2jamo._cffi import lib

        unicode_size = array('u').itemsize
        if unicode_size == 4:
            _calcsize = lib.hypua_jc2p_ucs4_calcsize
        elif unicode_size == 2:
            _calcsize = lib.hypua_jc2p_ucs2_calcsize
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

    def test_jc2p_decode(self):
        from cffi import FFI
        from hypua2jamo._cffi import lib

        unicode_size = array('u').itemsize
        if unicode_size == 4:
            _translate = lib.hypua_jc2p_ucs4_decode
            _calcsize = lib.hypua_jc2p_ucs4_calcsize
        elif unicode_size == 2:
            _translate = lib.hypua_jc2p_ucs2_decode
            _calcsize = lib.hypua_jc2p_ucs2_calcsize
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


class JamoEncoderTestBase(object):

    PUA_STRING = Fixtures.HunMinPreface.pua_string

    def test_p2j_encoder(self):
        encoder = self.make_encoder()

        self.assertEquals(0, encoder.getstate())

        for chunk_size in range(1, 1 + len(self.PUA_STRING)):
            encoder.reset()

            pua_string = self.PUA_STRING

            jamo = u''

            while chunk_size <= len(pua_string):
                jamo += encoder.encode(pua_string[:chunk_size], False)
                pua_string = pua_string[chunk_size:]
            jamo += encoder.encode(pua_string, True)

            self.assertEquals(
                self.JAMO_STRING,
                jamo
            )


class ComposedJamoEncoderImplementationOnPurePythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_encoder(self):
        from hypua2jamo.p2j_encoder\
            import ComposedJamoEncoderImplementationOnPurePython
        return ComposedJamoEncoderImplementationOnPurePython()


class DecomposedJamoEncoderImplementationOnPurePythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo.p2j_encoder\
            import DecomposedJamoEncoderImplementationOnPurePython
        return DecomposedJamoEncoderImplementationOnPurePython()


class ComposedJamoEncoderImplementationOnCFFITest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_encoder(self):
        from hypua2jamo.p2j_encoder\
            import ComposedJamoEncoderImplementationOnCFFI
        return ComposedJamoEncoderImplementationOnCFFI()


class DecomposedJamoEncoderImplementationOnCFFITest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo.p2j_encoder\
            import DecomposedJamoEncoderImplementationOnCFFI
        return DecomposedJamoEncoderImplementationOnCFFI()


class ComposedJamoEncoderImplementationOnCythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_encoder(self):
        from hypua2jamo._cython\
            import ComposedJamoEncoderImplementationOnCython
        return ComposedJamoEncoderImplementationOnCython()


class DecomposedJamoEncoderImplementationOnCythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo._cython\
            import DecomposedJamoEncoderImplementationOnCython
        return DecomposedJamoEncoderImplementationOnCython()


class JamoDecoderTestBase(object):

    PUA_STRING = Fixtures.HunMinPreface.pua_string

    def test_j2p_decoder(self):
        decoder = self.make_decoder()

        self.assertEquals((b'', 0), decoder.getstate())

        for chunk_size in range(1, 1 + len(self.JAMO_STRING)):
            decoder.reset()

            jamo_string = self.JAMO_STRING

            pua = u''

            while chunk_size <= len(jamo_string):
                pua += decoder.decode(jamo_string[:chunk_size], False)
                jamo_string = jamo_string[chunk_size:]
            pua += decoder.decode(jamo_string, True)

            self.assertEquals(
                self.PUA_STRING,
                pua
            )


class ComposedJamoDecoderImplementationOnPurePythonTest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo.j2p_decoder\
            import ComposedJamoDecoderImplementationOnPurePython
        return ComposedJamoDecoderImplementationOnPurePython()


class ComposedJamoDecoderImplementationOnCFFITest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo.j2p_decoder\
            import ComposedJamoDecoderImplementationOnCFFI
        return ComposedJamoDecoderImplementationOnCFFI()


class DecomposedJamoDecoderImplementationOnPurePythonTest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_decoder(self):
        from hypua2jamo.j2p_decoder\
            import DecomposedJamoDecoderImplementationOnPurePython
        return DecomposedJamoDecoderImplementationOnPurePython()


class DecomposedJamoDecoderImplementationOnCFFITest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_decoder(self):
        from hypua2jamo.j2p_decoder\
            import DecomposedJamoDecoderImplementationOnCFFI
        return DecomposedJamoDecoderImplementationOnCFFI()


class ComposedJamoDecoderImplementationOnCythonTest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo._cython \
            import ComposedJamoDecoderImplementationOnCython

        return ComposedJamoDecoderImplementationOnCython()


class DecomposedJamoDecoderImplementationOnCythonTest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_decoder(self):
        from hypua2jamo._cython \
            import DecomposedJamoDecoderImplementationOnCython

        return DecomposedJamoDecoderImplementationOnCython()
