# -*- coding: utf-8 -*-


def translate(pua, composed=True):
    ''' Convert a unicode string with Hanyang-PUA codes
    to a Syllable-Initial-Peak-Final encoded unicode string.

    :param pua: a unicode string with Hanyang-PUA codes
    :param composed: the result should be composed as possible (default True)
    :return: Syllable-Initial-Peak-Final encoded unicode string
    '''

    codes = (ord(ch) for ch in pua)
    return codes2unicode(codes, composed)


def codes2unicode(codes, composed=True):
    ''' Convert Hanyang-PUA code iterable to Syllable-Initial-Peak-Final
    encoded unicode string.

    :param codes: an iterable of Hanyang-PUA code
    :param composed: the result should be composed as possible (default True)
    :return: Syllable-Initial-Peak-Final encoded unicode string
    '''
    if composed:
        import hypua2jamo.composed
        table = hypua2jamo.composed.table
    else:
        import hypua2jamo.decomposed
        table = hypua2jamo.decomposed.table

    return u''.join(table.get(code, unichr(code))
                    for code in codes)
