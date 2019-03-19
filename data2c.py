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
import io
import sys

from ktug_hanyang_pua.fileformats.table_text import load_mappings_as_text_table  # noqa
from ktug_hanyang_pua.fileformats.table_binary import dump_mappings_as_binary_table  # noqa
from ktug_hanyang_pua.fileformats.tree_binary import dump_tree_as_binary  # noqa
from ktug_hanyang_pua.models import Mapping
from ktug_hanyang_pua.table import switch_source_and_targets
from ktug_hanyang_pua.tree import build_tree


PY3 = sys.version_info.major == 3


def make_mapping_groups(mappings):
    mappings = {
        m.source[0]: m.target
        for m in mappings
    }
    mappings = sorted(mappings.items())

    group_start = None
    group_targets = None
    for mapping_source, mapping_target in mappings:
        if group_start is None:
            group_start = mapping_source
            group_targets = [mapping_target]
        elif group_start + len(group_targets) == mapping_source:
            group_targets.append(mapping_target)
        else:
            yield group_start, tuple(group_targets)
            group_start = mapping_source
            group_targets = [mapping_target]

    if group_start is not None:
        yield group_start, tuple(group_targets)


def mapping_to_header(prefix, mappings):
    pua_groups = make_mapping_groups(mappings)
    pua_groups = tuple(pua_groups)

    for pua_start, targets in pua_groups:
        pua_end = pua_start + len(targets)
        for index_in_group, target in enumerate(targets):
            pua_code = pua_start + index_in_group

            codepoints = ', '.join(
                ['0x{:04X}'.format(len(target))] +
                ['0x{:04x}'.format(code) for code in target]
            )
            yield 'static const unsigned short {}_{:04X}[] = {{ {} }};'.format(  # noqa
                prefix, pua_code, codepoints
            )

        yield 'static const unsigned short *{}_group_{:04X}[] = {{'.format(  # noqa
            prefix, pua_start,
        )
        for pua_code in range(pua_start, pua_end):
            yield '\t{}_{:04X},'.format(prefix, pua_code)
        yield '};'

    yield '#define lookup(code) \\'
    for pua_start, targets in pua_groups:
        pua_end = pua_start + len(targets)
        yield (
            '\t(0x{start:04X} <= code && code <= 0x{end:04X})?'
            '({prefix}_group_{start:04X}[code - 0x{start:04X}]): \\'.format(
                prefix=prefix,
                start=pua_start,
                end=(pua_end - 1),
            )
        )
    yield '\tNULL'


class Node(object):

    def __init__(self):
        self.children = {}
        self.pua_code = None
        self.jamo_seq = None

    @property
    def id(self):
        if not self.jamo_seq:
            return 'root'
        code_seq = [code for code in self.jamo_seq]
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


def nodelist_to_tree(nodelist):
    tree = []

    for link in nodelist:
        node = Node()
        node.pua_code = link.target
        tree.append(node)

        if link.parent >= 0:
            parent = tree[link.parent]
            parent.children[link.source] = node

        if link.parent >= 0:
            node.jamo_seq = parent.jamo_seq + (link.source,)
        else:
            node.jamo_seq = ()

    return tree[0]


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
    for jamo_code, node in sorted(root.children.iteritems()):
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
            for jamo_code in node.jamo_seq:
                yield '\t0x{:04x},'.format(jamo_code)
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
            yield '\t0x{:04x},'.format(node.jamo_seq[-1])
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


def open_text_input(filename):
    if PY3:
        return io.open(filename, 'r', encoding='utf-8')
    else:
        return io.open(filename, 'rb')


def read_mappings(filename):
    with open_text_input(filename) as fp:
        return tuple(
            m for m in load_mappings_as_text_table(fp)
            if isinstance(m, Mapping)
        )


def mappings_to_table(mappings):
    return {
        m.source[0]: u''.join(unichr(x) for x in m.target)
        for m in mappings
    }


def build_nodelist(mappings):
    nodelist, __ = build_tree(
        Mapping(
            source=m.source,
            target=m.target[0],
            comment=m.comment,
        ) for m in mappings
    )
    return nodelist


if __name__ == '__main__':
    p2jc_mappings = read_mappings('data/hypua2jamocomposed.txt')
    with io.open('src/hypua2jamo/p2jc.bin', 'wb') as fp:
        dump_mappings_as_binary_table(p2jc_mappings, fp)
    jc2p_mappings = switch_source_and_targets(p2jc_mappings)
    jc2p_nodelist = build_nodelist(jc2p_mappings)
    with io.open('src/hypua2jamo/jc2p.bin', 'wb') as fp:
        dump_tree_as_binary(jc2p_nodelist, fp)
    with io.open('src/hypua2jamo-c/p2jc-table.h', 'wb') as fp:
        for line in mapping_to_header('p2jc', p2jc_mappings):
            fp.write(line)
            fp.write('\n')
    jc2p_tree = nodelist_to_tree(jc2p_nodelist)
    with io.open('src/hypua2jamo-c/jc2p-tree.inc', 'wb') as fp:
        for line in tree_to_header(jc2p_tree):
            fp.write(line.encode('utf-8'))
            fp.write('\n')

    p2jd_mappings = read_mappings('data/hypua2jamodecomposed.txt')
    with io.open('src/hypua2jamo/p2jd.bin', 'wb') as fp:
        dump_mappings_as_binary_table(p2jd_mappings, fp)
    jd2p_mappings = switch_source_and_targets(p2jd_mappings)
    jd2p_nodelist = build_nodelist(jd2p_mappings)
    with io.open('src/hypua2jamo/jd2p.bin', 'wb') as fp:
        dump_tree_as_binary(jd2p_nodelist, fp)
    with io.open('src/hypua2jamo-c/p2jd-table.h', 'wb') as fp:
        for line in mapping_to_header('p2jd', p2jd_mappings):
            fp.write(line)
            fp.write('\n')
    jd2p_tree = nodelist_to_tree(jd2p_nodelist)
    with io.open('src/hypua2jamo-c/jd2p-tree.inc', 'wb') as fp:
        for line in tree_to_header(jd2p_tree):
            fp.write(line.encode('utf-8'))
            fp.write('\n')

    d2c_mappings = read_mappings('data/jamocompose.map')
    c2d_mappings = tuple(switch_source_and_targets(d2c_mappings))
    with io.open('src/hypua2jamo/c2d.bin', 'wb') as fp:
        dump_mappings_as_binary_table(c2d_mappings, fp)
    d2c_nodelist = build_nodelist(d2c_mappings)
    with io.open('src/hypua2jamo/d2c.bin', 'wb') as fp:
        dump_tree_as_binary(d2c_nodelist, fp)
    with io.open('src/hypua2jamo-c/c2d-table.h', 'wb') as fp:
        for line in mapping_to_header('c2d', c2d_mappings):
            fp.write(line)
            fp.write('\n')
    d2c_tree = nodelist_to_tree(d2c_nodelist)
    with io.open('src/hypua2jamo-c/d2c-tree.inc', 'wb') as fp:
        for line in tree_to_header(d2c_tree):
            fp.write(line.encode('utf-8'))
            fp.write('\n')
