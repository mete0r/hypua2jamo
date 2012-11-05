# -*- coding: utf-8 -*-
import sys
import logging


logger = logging.getLogger(__name__)
jython = sys.platform.startswith('java')


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
    table = get_table(composed)
    return u''.join(table.get(code, unichr(code))
                    for code in codes)


tables = dict()


def get_table(composed):
    table = tables.get(composed)

    if not jython:
        if table is None:
            table = import_table(composed)
            if table is not None:
                tables[composed] = table

    if table is None:
        table = load_table(composed)
        if table is not None:
            tables[composed] = table

    return table


def import_table(composed):
    try:
        if composed:
            from hypua2jamo.composed import table
            return table
        else:
            from hypua2jamo.decomposed import table
            return table
    except Exception, e:
        logger.exception(e)
        return None


def load_table(composed):
    import os.path
    try:
        import cPickle
        pickle = cPickle
    except ImportError:
        import pickle

    if composed:
        filename = 'composed.pickle'
    else:
        filename = 'decomposed.pickle'
    path = os.path.join(os.path.dirname(__file__), filename)

    f = file(path)
    try:
        return pickle.load(f)
    finally:
        f.close()
