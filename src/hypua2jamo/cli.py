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
from argparse import ArgumentParser
from shutil import copyfileobj
import gettext
import io
import logging
import os.path
import sys

# PYTHON_ARGCOMPLETE_OK
try:
    import argcomplete
except ImportError:
    argcomplete = None

from . import __version__
from .encoder import ComposedJamoEncoder
from .encoder import DecomposedJamoEncoder
from .encoder import DecomposingEncoder
from .decoder import ComposedJamoDecoder
from .decoder import DecomposedJamoDecoder
from .decoder import ComposingDecoder

PY3 = sys.version_info.major == 3
logger = logging.getLogger(__name__)

locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
t = gettext.translation('hypua2jamo', locale_dir, fallback=True)
if PY3:
    _ = t.gettext
else:
    _ = t.ugettext


def main():
    gettext.gettext = t.gettext
    parser = main_argparse()
    if argcomplete:
        argcomplete.autocomplete(parser)
    args = parser.parse_args()
    configureLogging(args.verbose)
    logger.info('args: %s', args)

    if args.source is None:
        logger.error(_('Source encoding not specified (-s).'))
        raise SystemExit(1)
    if args.target is None:
        logger.error(_('Target encoding not specified (-t).'))
        raise SystemExit(1)

    source = args.source.lower()
    target = args.target.lower()

    if source == target:
        translator_class = None
    elif source == 'composed':
        if target == 'decomposed':
            translator_class = DecomposingEncoder
        elif target == 'pua':
            translator_class = ComposedJamoDecoder
        else:
            logger.error(_('Unsupported target encoding: %s'), args.target)
            raise SystemExit(1)
    elif source == 'decomposed':
        if target == 'composed':
            translator_class = ComposingDecoder
        elif target == 'pua':
            translator_class = DecomposedJamoDecoder
        else:
            logger.error(_('Unsupported target encoding: %s'), args.target)
            raise SystemExit(1)
    elif source == 'pua':
        if target == 'composed':
            translator_class = ComposedJamoEncoder
        elif target == 'decomposed':
            translator_class = DecomposedJamoEncoder
        else:
            logger.error(_('Unsupported target encoding: %s'), args.target)
            raise SystemExit(1)
    else:
        logger.error(_('Unsupported source encoding: %s'), args.source)
        raise SystemExit(1)

    if translator_class is None:
        with io.open(args.FILE, 'rb') as fp:
            copyfileobj(fp, sys.stdout)
        logger.warning(_('No conversion occured.'))
        return

    translator = translator_class()
    try:
        translate = translator.encode
    except AttributeError:
        translate = translator.decode

    with io.open(args.FILE, 'r', encoding='utf-8') as fp:
        for encoded in (translate(line) for line in fp):
            sys.stdout.write(encoded.encode('utf-8'))
        encoded = translate('', final=True)
        sys.stdout.write(encoded.encode('utf-8'))


def main_argparse():
    parser = ArgumentParser()
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help=_('output version information and exit')
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        help=_('increase verbosity')
    )
    parser.add_argument(
        '-s', '--source',
        action='store',
        help=_('source encoding (composed, decomposed, PUA)'),
    )
    parser.add_argument(
        '-t', '--target',
        action='store',
        help=_('target encoding (composed, decomposed, PUA)'),
    )
    parser.add_argument(
        'FILE',
        action='store',
        help=_('input file (UTF-8)'),
    )
    return parser


def configureLogging(verbosity):
    if verbosity == 1:
        level = logging.INFO
    elif verbosity > 1:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    try:
        import coloredlogs
    except ImportError:
        logging.basicConfig(level=level)
    else:
        coloredlogs.install(level)
