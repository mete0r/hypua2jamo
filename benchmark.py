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
from __future__ import unicode_literals
import io
import platform
import time

from hypua2jamo.j2p_decoder import ComposedJamo2PUAIncrementalDecoderPurePythonImplementation  # noqa
from hypua2jamo.j2p_decoder import ComposedJamo2PUAIncrementalDecoderCFFIImplementation  # noqa
from hypua2jamo._cython import ComposedJamo2PUAIncrementalDecoderCythonImplementation  # noqa
from hypua2jamo.p2j_encoder import PUA2JamoComposedIncrementalEncoderPurePythonImplementation  # noqa
from hypua2jamo.p2j_encoder import PUA2JamoComposedIncrementalEncoderCFFIImplementation  # noqa
from hypua2jamo._cython import PUA2JamoComposedIncrementalEncoderCythonImplementation  # noqa


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


def main():
    filename = '.benchmark.csv.{}'.format(time.time())

    N = 1000
    M = 100

    with io.open(filename, 'w', encoding='utf-8') as fp:
        j2p_decoder_classes = [
            ComposedJamo2PUAIncrementalDecoderPurePythonImplementation,
            ComposedJamo2PUAIncrementalDecoderCFFIImplementation,
            ComposedJamo2PUAIncrementalDecoderCythonImplementation,
        ]
        for decoder_class in j2p_decoder_classes:
            elapsed_total = 0
            for i in range(N):
                decoder = decoder_class()
                elapsed = time.time()
                try:
                    decoder.decode(
                        Fixtures.HunMinPreface.composed_jamo_string * M,
                        final=True
                    )
                finally:
                    elapsed = time.time() - elapsed
                elapsed_total += elapsed
            elapsed_average = elapsed_total / N
            elapsed_average *= 1000000
            elapsed_average += 0.5
            elapsed_average = int(elapsed_average)
            elapsed_average /= 1000000.0
            fp.write('{},{},{},{},{}\n'.format(
                platform.python_implementation(),
                platform.python_version(),
                platform.platform(),
                decoder_class.__name__,
                elapsed_average,
            ))

        encoder_classes = [
            PUA2JamoComposedIncrementalEncoderPurePythonImplementation,
            PUA2JamoComposedIncrementalEncoderCFFIImplementation,
            PUA2JamoComposedIncrementalEncoderCythonImplementation,
        ]
        for encoder_class in encoder_classes:
            elapsed_total = 0
            for i in range(N):
                encoder = encoder_class()
                elapsed = time.time()
                try:
                    encoder.encode(
                        Fixtures.HunMinPreface.pua_string * M,
                        final=True
                    )
                finally:
                    elapsed = time.time() - elapsed
                elapsed_total += elapsed
            elapsed_average = elapsed_total / N
            elapsed_average *= 1000000
            elapsed_average += 0.5
            elapsed_average = int(elapsed_average)
            elapsed_average /= 1000000.0
            fp.write('{},{},{},{},{}\n'.format(
                platform.python_implementation(),
                platform.python_version(),
                platform.platform(),
                encoder_class.__name__,
                elapsed_average,
            ))


if __name__ == '__main__':
    main()
