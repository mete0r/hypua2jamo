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
import io
import sys

from parsec import joint
from parsec import optional
from parsec import regex
from parsec import sepBy
from parsec import string
from parsec import spaces
from parsec import try_choice


#
# Parser combinators
#

comment = string('%%%') >> optional(spaces()) >> regex('.*')
codepoint_hex = regex('[0-9A-F]+').parsecmap(lambda x: int(x, 16))
codepoint = string('U+') >> codepoint_hex
codepoint_seq = sepBy(codepoint, spaces()).parsecmap(tuple)
arrow = string('=>')
mapping = joint(
    codepoint_seq,
    optional(spaces()) >> arrow << optional(spaces()),
    codepoint_seq,
    optional(comment),
).parsecmap(lambda x: (x[0], x[2], x[3]))

Line = try_choice(
    mapping,
    try_choice(
        comment,
        spaces().parsecmap(lambda x: ''),
    )
)


def main():
    s = '1107'
    assert codepoint_hex.parse(s) == 0x1107
    s = 'U+1107'
    assert codepoint.parse(s) == 0x1107
    s = 'U+1107 U+1107 U+110B'
    assert codepoint_seq.parse(s) == (0x1107, 0x1107, 0x110B)
    s = 'U+1107 U+1107 U+110B => U+112C'
    assert mapping.parse(s) == ((0x1107, 0x1107, 0x110B), (0x112C,), None)
    s = 'U+11BC U+11A8 U+11A8 => U+11ED %%% legacy encoding'
    assert mapping.parse(s) == ((0x11BC, 0x11A8, 0x11A8), (0x11ED,), 'legacy encoding')  # noqa
    assert Line.parse(s) == ((0x11BC, 0x11A8, 0x11A8), (0x11ED,), 'legacy encoding')  # noqa
    assert Line.parse('') == ''
    assert Line.parse('%%%') == ''
    assert Line.parse('%%% Trailing Consonants') == 'Trailing Consonants'

    inputfilename = sys.argv[1]
    with io.open(inputfilename, 'rb') as fp:
        lines = (
            Line.parse(line) for line in fp
        )
        lines = tuple(line for line in lines if line)
    for line in lines:
        print(line)


def parse_line(line):
    line = str(line)
    return Line.parse(line)


def parse_lines(lines):
    for line in lines:
        yield parse_line(line)


def parse_file(filename):
    with io.open(filename, 'r', encoding='utf-8') as fp:
        for e in parse_lines(fp):
            yield e


if __name__ == '__main__':
    main()
