# -*- coding: utf-8 -*-
# hypua2jamo: Convert Hanyang-PUA code to unicode Hangul Jamo
# Copyright (C) 2012,2018  mete0r
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
from __future__ import unicode_literals
from __future__ import print_function
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


def parse_datafile_into_table(f):
    if isinstance(f, basestring):
        with file(f) as f:
            return parse_datafile_into_table(f)
    return dict(parse_lines(f))


def table_to_header(table):
    pua_groups = make_groups(sorted(table.keys()))

    for pua_start, pua_end in pua_groups:
        for pua_code in range(pua_start, pua_end + 1):
            jamo = table[pua_code]

            codepoints = ', '.join(
                ['0x{:04X}'.format(len(jamo))] +
                ['0x{:04x}'.format(ord(uch)) for uch in jamo]
            )
            yield 'static const codepoint_t pua2jamo_{:04X}[] = {{ {} }};'.format(  # noqa
                pua_code, codepoints
            )

        yield 'static const codepoint_t *pua2jamo_group_{:04X}[] = {{'.format(
            pua_start,
        )
        for pua_code in range(pua_start, pua_end + 1):
            yield '\tpua2jamo_{:04X},'.format(pua_code)
        yield '};'

    yield '#define lookup(code) \\'
    for pua_start, pua_end in pua_groups:
        yield (
            '\t(0x{start:04X} <= code && code <= 0x{end:04X})?'
            '(pua2jamo_group_{start:04X}[code - 0x{start:04X}]): \\'.format(
                start=pua_start,
                end=pua_end
            )
        )
    yield '\tNULL'


def make_groups(codes):
    groups = []
    current_group = None
    for code in codes:
        if current_group is None:
            current_group = [code, code]
        elif current_group[-1] + 1 == code:
            current_group[-1] = code
        else:
            groups.append(current_group)
            current_group = [code, code]

    if current_group is not None:
        groups.append(current_group)

    return groups


class Node(object):

    def __init__(self):
        self.children = {}
        self.pua_code = None
        self.jamo_seq = None

    @property
    def id(self):
        if not self.jamo_seq:
            return 'root'
        code_seq = [ord(ch) for ch in self.jamo_seq]
        return ''.join('u{:4x}'.format(code) for code in code_seq)

    def __repr__(self):
        if self.pua_code is not None:
            if self.children:
                return str('[{:04x}] -> {}'.format(
                    self.pua_code, self.children,
                ))
            else:
                return str('[{:04x}]'.format(self.pua_code))
        return repr(self.children)


def table_to_tree(table):
    root = Node()
    root.jamo_seq = ''
    for pua_code, jamo_chars in table.iteritems():
        node = root
        jamo_seq = ''
        for jamo_char in jamo_chars:
            node = node.children.setdefault(jamo_char, Node())
            jamo_seq += jamo_char
            node.jamo_seq = jamo_seq
        node.pua_code = pua_code
    return root


def tree_dfs(root):
    for jamo_char, node in sorted(root.children.iteritems()):
        for res in tree_dfs(node):
            yield res
    yield root


def tree_to_header(tree):
    for node in tree_dfs(tree):
        children = sorted([
            child.id for child in node.children.values()
        ])
        if len(children) > 0:
            yield 'static struct Node* node_{}_children[] = {{'.format(node.id)
            for child_id in children:
                yield '\t&node_{},'.format(child_id)
            yield '};'

        yield 'static struct Node node_{} = {{'.format(node.id)
        if len(node.jamo_seq) > 0:
            yield '\t0x{:04x},'.format(ord(node.jamo_seq[-1]))
        else:
            yield '\t0,'
        if node.pua_code is not None:
            yield '\t0x{:04x},'.format(node.pua_code)
        else:
            yield '\t0,'
        yield '\t{},'.format(len(children))
        if len(children) > 0:
            yield '\tnode_{}_children'.format(node.id)
        else:
            yield '\t0'
        yield '};'


if __name__ == '__main__':
    composed = parse_datafile_into_table(
        '../../data/hypua2jamocomposed.txt'
    )
    jc2p_tree = table_to_tree(composed)
    with io.open('jc2p-tree.h', 'wb') as fp:
        with io.open('jc2p-tree.h.in', 'rb') as rfp:
            for line in rfp:
                fp.write(line)
        for line in tree_to_header(jc2p_tree):
            fp.write(line.encode('utf-8'))
            fp.write('\n')
    with io.open('p2jc-table.h', 'wb') as fp:
        for line in table_to_header(composed):
            fp.write(line)
            fp.write('\n')

    decomposed = parse_datafile_into_table(
        '../../data/hypua2jamodecomposed.txt'
    )
    with io.open('p2jd-table.h', 'wb') as fp:
        for line in table_to_header(decomposed):
            fp.write(line)
            fp.write('\n')
