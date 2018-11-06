# -*- coding: utf-8 -*-
# hypua2jamo: Convert Hanyang-PUA code to unicode Hangul Jamo
# Copyright (C) 2012  mete0r
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


def test_parse(self):
    lines = ['U+E0BC => U+115F U+1161 U+11AE',
             'U+E0C6 => U+115F U+11A3',
             'U+E230 => U+1102 U+117A %%% <= U+1102 U+117C',
             'U+F86A =>']

    pua, jamo = parse_line(lines[0])
    self.assertEquals(0xE0BC, pua)
    self.assertEquals(unichr(0x115F)+unichr(0x1161)+unichr(0x11AE), jamo)

    pua, jamo = parse_line(lines[2])
    self.assertEquals(0xE230, pua)
    self.assertEquals(unichr(0x1102)+unichr(0x117A), jamo)

    pua, jamo = parse_line(lines[3])
    self.assertEquals(0xF86A, pua)
    self.assertEquals(u'', jamo)


def codepoint(code):
    return '\\u%x' % code


def parse_datafile_into_table(f):
    if isinstance(f, basestring):
        with file(f) as f:
            return parse_datafile_into_table(f)
    return dict(parse_lines(f))


def table_to_pickle(table, f):
    if isinstance(f, basestring):
        with file(f, 'w') as f:
            return table_to_pickle(table, f)

    import cPickle
    cPickle.dump(table, f)


def table_to_py(table, f):
    if isinstance(f, basestring):
        with file(f, 'w') as f:
            return table_to_py(table, f)

    f.write('# -*- coding: utf-8 -*-\n\ntable = {\n')
    for pua, jamo in table.items():

        pua = '0x%x' % pua

        comment = "u'%s'" % jamo.encode('utf-8')

        jamo = ''.join(codepoint(ord(ch)) for ch in jamo)
        jamo = "u'"+jamo+"'"

        line = ' '*4 + '%s: %s,' % (pua, jamo)
        line += ' '*(max(60 - len(line), 2))
        line += '# %s\n' % comment
        f.write(line)
    f.write('}\n')


if __name__ == '__main__':
    composed = parse_datafile_into_table('data/hypua2jamocomposed.txt')
    table_to_py(composed, 'src/hypua2jamo/composed.py')
    table_to_pickle(composed, 'src/hypua2jamo/composed.pickle')

    decomposed = parse_datafile_into_table('data/hypua2jamodecomposed.txt')
    table_to_py(decomposed, 'src/hypua2jamo/decomposed.py')
    table_to_pickle(decomposed, 'src/hypua2jamo/decomposed.pickle')
