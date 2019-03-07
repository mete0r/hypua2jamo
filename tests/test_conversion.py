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

        self.assertEqual(expected, result)

    def test_translate_composed(self):
        from hypua2jamo import translate

        jamo_string = translate(
            Fixtures.HunMinPreface.pua_string,
        )
        self.assertEqual(
            Fixtures.HunMinPreface.composed_jamo_string,
            jamo_string,
        )

    def test_translate_decomposed(self):
        from hypua2jamo import translate

        jamo_string = translate(
            Fixtures.HunMinPreface.pua_string,
            composed=False
        )
        self.assertEqual(
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

        self.assertEqual(1, calcsize(self.jamo_string[:1]))    # 나
        self.assertEqual(2, calcsize(self.jamo_string[:2]))    # 랏
        self.assertEqual(3, calcsize(self.jamo_string[:3]))
        self.assertEqual(4, calcsize(self.jamo_string[:4]))
        self.assertEqual(5, calcsize(self.jamo_string[:5]))
        self.assertEqual(6, calcsize(self.jamo_string[:6]))
        self.assertEqual(6, calcsize(self.jamo_string[:7]))
        self.assertEqual(7, calcsize(self.jamo_string[:8]))
        self.assertEqual(8, calcsize(self.jamo_string[:9]))
        self.assertEqual(9, calcsize(self.jamo_string[:10]))
        self.assertEqual((
            u'나랏\u302e말\u302f\uebd4미\u302e '
        ), self.pua_string[:9])

        self.assertEqual(10, calcsize(self.jamo_string[:11]))  # 中
        self.assertEqual(11, calcsize(self.jamo_string[:12]))
        self.assertEqual(12, calcsize(self.jamo_string[:13]))
        self.assertEqual(11, calcsize(self.jamo_string[:14]))
        self.assertEqual(12, calcsize(self.jamo_string[:15]))  # 國
        self.assertEqual(13, calcsize(self.jamo_string[:16]))  # 귁
        self.assertEqual(14, calcsize(self.jamo_string[:17]))  # 에
        self.assertEqual(15, calcsize(self.jamo_string[:18]))  # u302e
        self.assertEqual(16, calcsize(self.jamo_string[:19]))  # u0020

        self.assertEqual(17, calcsize(self.jamo_string[:20]))  # 달
        self.assertEqual(18, calcsize(self.jamo_string[:21]))  # 아
        self.assertEqual(19, calcsize(self.jamo_string[:22]))  # u302e
        self.assertEqual(20, calcsize(self.jamo_string[:23]))  # u0020
        self.assertEqual((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
        ), self.pua_string[:20])

        self.assertEqual(21, calcsize(self.jamo_string[:24]))  # 문
        self.assertEqual(22, calcsize(self.jamo_string[:25]))  #
        self.assertEqual(22, calcsize(self.jamo_string[:26]))  #
        self.assertEqual(22, calcsize(self.jamo_string[:27]))  #
        self.assertEqual(23, calcsize(self.jamo_string[:28]))  # 와
        self.assertEqual(24, calcsize(self.jamo_string[:29]))  # u302e
        self.assertEqual(25, calcsize(self.jamo_string[:30]))  # 로
        self.assertEqual(26, calcsize(self.jamo_string[:31]))  # u0020
        self.assertEqual((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
        ), self.pua_string[:26])

        self.assertEqual(27, calcsize(self.jamo_string[:32]))  # 서
        self.assertEqual(28, calcsize(self.jamo_string[:33]))  # 르
        self.assertEqual(29, calcsize(self.jamo_string[:34]))  # u0020
        self.assertEqual((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
            u'서르 '
        ), self.pua_string[:29])

        self.assertEqual(30, calcsize(self.jamo_string[:35]))
        self.assertEqual(30, calcsize(self.jamo_string[:36]))
        self.assertEqual(31, calcsize(self.jamo_string[:37]))
        self.assertEqual(31, calcsize(self.jamo_string[:38]))
        self.assertEqual(31, calcsize(self.jamo_string[:39]))
        self.assertEqual(32, calcsize(self.jamo_string[:40]))  # 디
        self.assertEqual(33, calcsize(self.jamo_string[:41]))  # u302e
        self.assertEqual(34, calcsize(self.jamo_string[:42]))  # u0020
        self.assertEqual((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
            u'서르 \ue97d\ue570디\u302e '
        ), self.pua_string[:34])

        self.assertEqual(35, calcsize(self.jamo_string[:43]))  # 아
        self.assertEqual(36, calcsize(self.jamo_string[:44]))  # 니
        self.assertEqual(37, calcsize(self.jamo_string[:45]))  # u302e
        self.assertEqual(38, calcsize(self.jamo_string[:46]))
        self.assertEqual(38, calcsize(self.jamo_string[:47]))
        self.assertEqual(38, calcsize(self.jamo_string[:48]))
        self.assertEqual(39, calcsize(self.jamo_string[:49]))
        self.assertEqual(39, calcsize(self.jamo_string[:50]))
        self.assertEqual(40, calcsize(self.jamo_string[:51]))  # 302e
        self.assertEqual((
            u'나랏\u302e말\u302f\uebd4미\u302e '
            u'中\ue35f國귁에\u302e 달아\u302e '
            u'문\uf258와\u302e로 '
            u'서르 \ue97d\ue570디\u302e '
            u'아니\u302e\uf53c\uebe1\u302e'
        ), self.pua_string[:40])

        self.assertEqual(40, calcsize(self.jamo_string))

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

        self.assertEqual(pua[:1], translate(jamo[:1]))    # 나
        self.assertEqual(pua[:2], translate(jamo[:2]))    # 랏
        self.assertEqual(pua[:3], translate(jamo[:3]))
        self.assertEqual(pua[:4], translate(jamo[:4]))
        self.assertEqual(pua[:5], translate(jamo[:5]))
        self.assertEqual(pua[:5] + u'\uf7ca', translate(jamo[:6]))
        self.assertEqual(pua[:6], translate(jamo[:7]))
        self.assertEqual(pua[:7], translate(jamo[:8]))
        self.assertEqual(pua[:8], translate(jamo[:9]))
        self.assertEqual(pua[:9], translate(jamo[:10]))

        self.assertEqual(pua[:10], translate(jamo[:11]))  # 中
        self.assertEqual(pua[:10] + u'\uf790', translate(jamo[:12]))
        self.assertEqual(pua[:10] + u'\u1103\u1172', translate(jamo[:13]))
        self.assertEqual(pua[:11], translate(jamo[:14]))
        self.assertEqual(pua[:12], translate(jamo[:15]))  # 國
        self.assertEqual(pua[:13], translate(jamo[:16]))  # 귁
        self.assertEqual(pua[:14], translate(jamo[:17]))  # 에
        self.assertEqual(pua[:15], translate(jamo[:18]))  # u302e
        self.assertEqual(pua[:16], translate(jamo[:19]))  # u0020

        self.assertEqual(pua[:17], translate(jamo[:20]))  # 달
        self.assertEqual(pua[:18], translate(jamo[:21]))  # 아
        self.assertEqual(pua[:19], translate(jamo[:22]))  # u302e
        self.assertEqual(pua[:20], translate(jamo[:23]))  # u0020

        self.assertEqual(pua[:21], translate(jamo[:24]))  # 문
        self.assertEqual(pua[:21] + u'\uf7ea', translate(jamo[:25]))  #
        self.assertEqual(pua[:21] + u'\uf250', translate(jamo[:26]))  #
        self.assertEqual(pua[:22], translate(jamo[:27]))  #
        self.assertEqual(pua[:23], translate(jamo[:28]))  # 와
        self.assertEqual(pua[:24], translate(jamo[:29]))  # u302e
        self.assertEqual(pua[:25], translate(jamo[:30]))  # 로
        self.assertEqual(pua[:26], translate(jamo[:31]))  # u0020

        self.assertEqual(pua[:27], translate(jamo[:32]))  # 서
        self.assertEqual(pua[:28], translate(jamo[:33]))  # 르
        self.assertEqual(pua[:29], translate(jamo[:34]))  # u0020

        self.assertEqual(pua[:29] + u'\uf7c2', translate(jamo[:35]))
        self.assertEqual(pua[:30], translate(jamo[:36]))
        self.assertEqual(pua[:30] + u'\uf7a8', translate(jamo[:37]))
        self.assertEqual(pua[:30] + u'\ue560', translate(jamo[:38]))
        self.assertEqual(pua[:31], translate(jamo[:39]))
        self.assertEqual(pua[:32], translate(jamo[:40]))  # 디
        self.assertEqual(pua[:33], translate(jamo[:41]))  # u302e
        self.assertEqual(pua[:34], translate(jamo[:42]))  # u0020

        self.assertEqual(pua[:35], translate(jamo[:43]))  # 아
        self.assertEqual(pua[:36], translate(jamo[:44]))  # 니
        self.assertEqual(pua[:37], translate(jamo[:45]))  # u302e
        self.assertEqual(pua[:37] + u'\uf7fc', translate(jamo[:46]))
        self.assertEqual(pua[:37] + u'\uf537', translate(jamo[:47]))
        self.assertEqual(pua[:38], translate(jamo[:48]))
        self.assertEqual(pua[:38] + u'\uf7ca', translate(jamo[:49]))
        self.assertEqual(pua[:39], translate(jamo[:50]))
        self.assertEqual(pua[:40], translate(jamo[:51]))  # 302e

        self.assertEqual(pua[:40], translate(jamo))


class JamoEncoderTestBase(object):

    PUA_STRING = Fixtures.HunMinPreface.pua_string

    def test_encoder(self):
        encoder = self.make_encoder()

        self.assertEqual(0, encoder.getstate())

        for chunk_size in range(1, 1 + len(self.PUA_STRING)):
            encoder.reset()

            pua_string = self.PUA_STRING

            jamo = u''

            while chunk_size <= len(pua_string):
                jamo += encoder.encode(pua_string[:chunk_size], False)
                pua_string = pua_string[chunk_size:]
            jamo += encoder.encode(pua_string, True)

            self.assertEqual(
                self.JAMO_STRING,
                jamo
            )


class ComposedJamoEncoderImplementationOnPurePythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_encoder(self):
        from hypua2jamo.encoder\
            import ComposedJamoEncoderImplementationOnPurePython
        return ComposedJamoEncoderImplementationOnPurePython()


class ComposedJamoEncoderImplementationOnCFFITest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_encoder(self):
        from hypua2jamo.encoder\
            import ComposedJamoEncoderImplementationOnCFFI
        return ComposedJamoEncoderImplementationOnCFFI()


class ComposedJamoEncoderImplementationOnCythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_encoder(self):
        from hypua2jamo._cython\
            import ComposedJamoEncoderImplementationOnCython
        return ComposedJamoEncoderImplementationOnCython()


class DecomposedJamoEncoderImplementationOnPurePythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo.encoder\
            import DecomposedJamoEncoderImplementationOnPurePython
        return DecomposedJamoEncoderImplementationOnPurePython()


class DecomposedJamoEncoderImplementationOnCFFITest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo.encoder\
            import DecomposedJamoEncoderImplementationOnCFFI
        return DecomposedJamoEncoderImplementationOnCFFI()

    def test_f7ca(self):
        encoder = self.make_encoder()
        jamo = encoder.encode(u'\uf7ca', final=True)
        self.assertEqual(u'\u1109\u1109', jamo)


class DecomposedJamoEncoderImplementationOnCythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo._cython\
            import DecomposedJamoEncoderImplementationOnCython
        return DecomposedJamoEncoderImplementationOnCython()

    def test_f7ca(self):
        encoder = self.make_encoder()
        jamo = encoder.encode(u'\uf7ca', final=True)
        self.assertEqual(u'\u1109\u1109', jamo)


class DecomposingEncoderImplementationOnPurePythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    PUA_STRING = Fixtures.HunMinPreface.composed_jamo_string
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo.encoder\
            import DecomposingEncoderImplementationOnPurePython
        return DecomposingEncoderImplementationOnPurePython()


class DecomposingEncoderImplementationOnCFFITest(
    TestCase,
    JamoEncoderTestBase,
):
    PUA_STRING = Fixtures.HunMinPreface.composed_jamo_string
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo.encoder\
            import DecomposingEncoderImplementationOnCFFI
        return DecomposingEncoderImplementationOnCFFI()


class DecomposingEncoderImplementationOnCythonTest(
    TestCase,
    JamoEncoderTestBase,
):
    PUA_STRING = Fixtures.HunMinPreface.composed_jamo_string
    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_encoder(self):
        from hypua2jamo._cython\
            import DecomposingEncoderImplementationOnCython
        return DecomposingEncoderImplementationOnCython()


class JamoDecoderTestBase(object):

    PUA_STRING = Fixtures.HunMinPreface.pua_string

    def test_decoder(self):
        decoder = self.make_decoder()

        self.assertEqual((b'', 0), decoder.getstate())

        for chunk_size in range(1, 1 + len(self.JAMO_STRING)):
            decoder.reset()

            jamo_string = self.JAMO_STRING

            pua = u''

            while chunk_size <= len(jamo_string):
                pua += decoder.decode(jamo_string[:chunk_size], False)
                jamo_string = jamo_string[chunk_size:]
            pua += decoder.decode(jamo_string, True)

            self.assertEqual(
                self.PUA_STRING,
                pua
            )


class ComposedJamoDecoderTestBase(JamoDecoderTestBase):

    def test_jc2p_decode(self):
        def translate(jamo_string):
            decoder = self.make_decoder()
            return decoder.decode(jamo_string, final=True)

        pua = self.PUA_STRING
        jamo = self.JAMO_STRING

        self.assertEqual(pua[:1], translate(jamo[:1]))    # 나
        self.assertEqual(pua[:2], translate(jamo[:2]))    # 랏
        self.assertEqual(pua[:3], translate(jamo[:3]))
        self.assertEqual(pua[:4], translate(jamo[:4]))
        self.assertEqual(pua[:5], translate(jamo[:5]))
        self.assertEqual(pua[:5] + u'\uf7ca', translate(jamo[:6]))
        self.assertEqual(pua[:6], translate(jamo[:7]))
        self.assertEqual(pua[:7], translate(jamo[:8]))
        self.assertEqual(pua[:8], translate(jamo[:9]))
        self.assertEqual(pua[:9], translate(jamo[:10]))

        self.assertEqual(pua[:10], translate(jamo[:11]))  # 中
        self.assertEqual(pua[:10] + u'\uf790', translate(jamo[:12]))
        self.assertEqual(pua[:10] + u'\u1103\u1172', translate(jamo[:13]))
        self.assertEqual(pua[:11], translate(jamo[:14]))
        self.assertEqual(pua[:12], translate(jamo[:15]))  # 國
        self.assertEqual(pua[:13], translate(jamo[:16]))  # 귁
        self.assertEqual(pua[:14], translate(jamo[:17]))  # 에
        self.assertEqual(pua[:15], translate(jamo[:18]))  # u302e
        self.assertEqual(pua[:16], translate(jamo[:19]))  # u0020

        self.assertEqual(pua[:17], translate(jamo[:20]))  # 달
        self.assertEqual(pua[:18], translate(jamo[:21]))  # 아
        self.assertEqual(pua[:19], translate(jamo[:22]))  # u302e
        self.assertEqual(pua[:20], translate(jamo[:23]))  # u0020

        self.assertEqual(pua[:21], translate(jamo[:24]))  # 문
        self.assertEqual(pua[:21] + u'\uf7ea', translate(jamo[:25]))  #
        self.assertEqual(pua[:21] + u'\uf250', translate(jamo[:26]))  #
        self.assertEqual(pua[:22], translate(jamo[:27]))  #
        self.assertEqual(pua[:23], translate(jamo[:28]))  # 와
        self.assertEqual(pua[:24], translate(jamo[:29]))  # u302e
        self.assertEqual(pua[:25], translate(jamo[:30]))  # 로
        self.assertEqual(pua[:26], translate(jamo[:31]))  # u0020

        self.assertEqual(pua[:27], translate(jamo[:32]))  # 서
        self.assertEqual(pua[:28], translate(jamo[:33]))  # 르
        self.assertEqual(pua[:29], translate(jamo[:34]))  # u0020

        self.assertEqual(pua[:29] + u'\uf7c2', translate(jamo[:35]))
        self.assertEqual(pua[:30], translate(jamo[:36]))
        self.assertEqual(pua[:30] + u'\uf7a8', translate(jamo[:37]))
        self.assertEqual(pua[:30] + u'\ue560', translate(jamo[:38]))
        self.assertEqual(pua[:31], translate(jamo[:39]))
        self.assertEqual(pua[:32], translate(jamo[:40]))  # 디
        self.assertEqual(pua[:33], translate(jamo[:41]))  # u302e
        self.assertEqual(pua[:34], translate(jamo[:42]))  # u0020

        self.assertEqual(pua[:35], translate(jamo[:43]))  # 아
        self.assertEqual(pua[:36], translate(jamo[:44]))  # 니
        self.assertEqual(pua[:37], translate(jamo[:45]))  # u302e
        self.assertEqual(pua[:37] + u'\uf7fc', translate(jamo[:46]))
        self.assertEqual(pua[:37] + u'\uf537', translate(jamo[:47]))
        self.assertEqual(pua[:38], translate(jamo[:48]))
        self.assertEqual(pua[:38] + u'\uf7ca', translate(jamo[:49]))
        self.assertEqual(pua[:39], translate(jamo[:50]))
        self.assertEqual(pua[:40], translate(jamo[:51]))  # 302e

        self.assertEqual(pua[:40], translate(jamo))


class ComposedJamoDecoderImplementationOnPurePythonTest(
    TestCase,
    ComposedJamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo.decoder\
            import ComposedJamoDecoderImplementationOnPurePython
        return ComposedJamoDecoderImplementationOnPurePython()


class ComposedJamoDecoderImplementationOnCFFITest(
    TestCase,
    ComposedJamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo.decoder\
            import ComposedJamoDecoderImplementationOnCFFI
        return ComposedJamoDecoderImplementationOnCFFI()


class ComposedJamoDecoderImplementationOnCythonTest(
    TestCase,
    ComposedJamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo._cython \
            import ComposedJamoDecoderImplementationOnCython

        return ComposedJamoDecoderImplementationOnCython()


class DecomposedJamoDecoderImplementationOnPurePythonTest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_decoder(self):
        from hypua2jamo.decoder\
            import DecomposedJamoDecoderImplementationOnPurePython
        return DecomposedJamoDecoderImplementationOnPurePython()


class DecomposedJamoDecoderImplementationOnCFFITest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_decoder(self):
        from hypua2jamo.decoder\
            import DecomposedJamoDecoderImplementationOnCFFI
        return DecomposedJamoDecoderImplementationOnCFFI()


class DecomposedJamoDecoderImplementationOnCythonTest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string

    def make_decoder(self):
        from hypua2jamo._cython \
            import DecomposedJamoDecoderImplementationOnCython

        return DecomposedJamoDecoderImplementationOnCython()


class ComposingDecoderImplementationOnPurePythonTest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string
    PUA_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo.decoder\
            import ComposingDecoderImplementationOnPurePython
        return ComposingDecoderImplementationOnPurePython()


class ComposingDecoderImplementationOnCFFITest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string
    PUA_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo.decoder\
            import ComposingDecoderImplementationOnCFFI
        return ComposingDecoderImplementationOnCFFI()


class ComposingDecoderImplementationOnCythonTest(
    TestCase,
    JamoDecoderTestBase
):

    JAMO_STRING = Fixtures.HunMinPreface.decomposed_jamo_string
    PUA_STRING = Fixtures.HunMinPreface.composed_jamo_string

    def make_decoder(self):
        from hypua2jamo._cython\
            import ComposingDecoderImplementationOnCython
        return ComposingDecoderImplementationOnCython()
