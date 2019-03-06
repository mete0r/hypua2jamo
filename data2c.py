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
from __future__ import unicode_literals
from __future__ import print_function
from struct import Struct
import io

import ktugfile


def table_to_pack(table):
    pua_groups = make_groups(sorted(table.keys()))

    pua_groups_length = len(pua_groups)
    pua_groups_length_struct = Struct('<I')
    yield pua_groups_length_struct.pack(pua_groups_length)

    group_entry_struct = Struct('<HH')
    for pua_start, pua_end in pua_groups:
        yield group_entry_struct.pack(pua_start, pua_end)

    for pua_start, pua_end in pua_groups:
        for pua_code in range(pua_start, pua_end + 1):
            jamo = table[pua_code]
            jamo_length = len(jamo)
            jamo_length_struct = Struct('<H')
            yield jamo_length_struct.pack(jamo_length)

            jamo_struct = Struct('<H')
            for uch in jamo:
                yield jamo_struct.pack(ord(uch))


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


def tree_bfs(root):
    q = [root]
    while len(q) > 0:
        node = q[0]
        q = q[1:]

        yield node
        children = [
            child for jamo, child in sorted(node.children.iteritems())
        ]
        q.extend(children)


def tree_dfs(root):
    for jamo_char, node in sorted(root.children.iteritems()):
        for res in tree_dfs(node):
            yield res
    yield root


def tree_to_header(tree):
    nodelist = list(tree_bfs(tree))
    assert nodelist[0] is tree
    for index, node in enumerate(nodelist):
        node.index = index

    for node in tree_dfs(tree):
        children = sorted([
            child.id for child in node.children.values()
        ])
        if len(children) > 0:
            yield 'static const struct Node *node_{}_children[] = {{'.format(
                node.id
            )
            for child_id in children:
                yield '\t&node_{},'.format(child_id)
            yield '};'

        if len(node.jamo_seq) > 0:
            yield 'static const uint16_t node_{}_jamo_seq[] = {{'.format(
                node.id
            )
            for jamo in node.jamo_seq:
                yield '\t0x{:04x},'.format(ord(jamo))
            yield '};'

        yield 'static const struct Node node_{} = {{'.format(node.id)

        # index
        yield '\t{},'.format(node.index)

        # jamo_seq_len
        yield '\t{},'.format(len(node.jamo_seq))

        # jamo_seq
        if len(node.jamo_seq) > 0:
            yield '\tnode_{}_jamo_seq,'.format(node.id)
        else:
            yield '\t0,'

        # jamo_code
        if len(node.jamo_seq) > 0:
            yield '\t0x{:04x},'.format(ord(node.jamo_seq[-1]))
        else:
            yield '\t0,'

        # pua_code
        if node.pua_code is not None:
            yield '\t0x{:04x},'.format(node.pua_code)
        else:
            yield '\t0,'

        # childrenLen
        yield '\t{},'.format(len(children))

        # children
        if len(children) > 0:
            yield '\tnode_{}_children,'.format(node.id)
        else:
            yield '\t0,'

        # node_name
        yield '\t"{}",'.format(node.id)

        yield '};'

    yield ''

    yield 'static const struct Node* nodelist[] = {'
    for node in nodelist:
        yield '\t&node_{},'.format(node.id)
    yield '};'


def tree_to_pack(tree):
    nodelist = list(tree_bfs(tree))
    assert nodelist[0] is tree
    for index, node in enumerate(nodelist):
        node.index = index

    # jamo_code, pua_code, parent id
    node_struct = Struct('<iHH')

    # whole tree (except the root node)
    for node in tree_bfs(tree):
        parent_id = node.index
        for jamo_char in sorted(node.children):
            jamo_code = ord(jamo_char)
            child = node.children[jamo_char]
            pua_code = child.pua_code or 0
            yield node_struct.pack(
                jamo_code,
                pua_code,
                parent_id,
            )


if __name__ == '__main__':
    composed = dict(ktugfile.parse_file(
        'data/hypua2jamocomposed.txt'
    ))
    jc2p_tree = table_to_tree(composed)
    with io.open('src/hypua2jamo-c/jc2p-tree.inc', 'wb') as fp:
        for line in tree_to_header(jc2p_tree):
            fp.write(line.encode('utf-8'))
            fp.write('\n')
    with io.open('src/hypua2jamo-c/p2jc-table.h', 'wb') as fp:
        for line in table_to_header(composed):
            fp.write(line)
            fp.write('\n')
    with io.open('src/hypua2jamo/p2jc.bin', 'wb') as fp:
        for pack in table_to_pack(composed):
            fp.write(pack)
    with io.open('src/hypua2jamo/jc2p.bin', 'wb') as fp:
        for pack in tree_to_pack(jc2p_tree):
            fp.write(pack)

    decomposed = dict(ktugfile.parse_file(
        'data/hypua2jamodecomposed.txt'
    ))
    with io.open('src/hypua2jamo-c/p2jd-table.h', 'wb') as fp:
        for line in table_to_header(decomposed):
            fp.write(line)
            fp.write('\n')
    with io.open('src/hypua2jamo/p2jd.bin', 'wb') as fp:
        for pack in table_to_pack(decomposed):
            fp.write(pack)
    jd2p_tree = table_to_tree(decomposed)
    with io.open('src/hypua2jamo-c/jd2p-tree.inc', 'wb') as fp:
        for line in tree_to_header(jd2p_tree):
            fp.write(line.encode('utf-8'))
            fp.write('\n')
    with io.open('src/hypua2jamo/jd2p.bin', 'wb') as fp:
        for pack in tree_to_pack(jd2p_tree):
            fp.write(pack)
