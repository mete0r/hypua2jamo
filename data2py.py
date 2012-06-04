# -*- coding: utf-8 -*-


def parse_line(line):
    comment = line.find('%%%')
    if comment != -1:
        line = line[:comment]

    if line.startswith('U+'):
        pua = int(line[2:6], 16)
        jamo = line[10:].strip()
        if jamo != '':
            jamo = jamo.split(' ')
            try:
                jamo = u''.join(unichr(int(code[2:6], 16)) for code in jamo)
            except:
                print line
                raise
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


def convert(source, dest):
    with file(dest, 'w') as g:
        g.write('# -*- coding: utf-8 -*-\n\ntable = {\n')
        with file(source, 'r') as f:
            for pua, jamo in parse_lines(f):

                pua = '0x%x' % pua

                comment = "u'%s'" % jamo.encode('utf-8')

                jamo = ''.join(codepoint(ord(ch)) for ch in jamo)
                jamo = "u'"+jamo+"'"

                line = ' '*4 + '%s: %s,' % (pua, jamo)
                line += ' '*(60 - len(line))
                line += '# %s\n' % comment
                g.write(line)
        g.write('}')


if __name__ == '__main__':
    convert('data/hypua2jamocomposed.txt', 'src/hypua2jamo/composed.py')
    convert('data/hypua2jamodecomposed.txt', 'src/hypua2jamo/decomposed.py')
