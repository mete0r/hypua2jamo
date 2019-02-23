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


def parse_line(line):
    comment = line.find('%%%')
    if comment != -1:
        line = line[:comment]

    if line.startswith('U+'):
        pua = int(line[2:6], 16)
        jamo = line[10:].strip()
        if jamo != '':
            jamo = jamo.split(' ')
            jamo = u''.join(unichr(int(code[2:6], 16)) for code in jamo)
        else:
            jamo = u''
        return pua, jamo
    else:
        return None, None


def parse_lines(lines):
    for line in lines:
        pua, jamo = parse_line(line)
        if pua:
            yield pua, jamo


def parse_file(filename):
    with io.open(filename, 'r', encoding='utf-8') as fp:
        for e in parse_lines(fp):
            yield e
