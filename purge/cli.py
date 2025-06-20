# Copyright (C) 2025 AuthorDriu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""cli.py
is a module for parsing command line arguments
"""


import argparse
import pathlib
import logging

import _meta


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=_meta.PACKAGE_NAME,
        description=_meta.LONG_DESCRIPTION
    )

    set_required_group(parser)
    set_logging_group(parser)

    return parser.parse_args()


def set_required_group(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group('required', 'required parameters')
    group.add_argument(
        '-t', '--target',
        type=existing_target, 
        required=True,
        help='path to the rotating file'
    )
    group.add_argument(
        '-s', '--size',
        type=unsigned_int,
        required=True,
        help='minimum size for performing rotation'
    )


def set_logging_group(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group('logging', 'logging configuration')
    group.add_argument(
        '-l', '--level',
        type=truncate_loglevel,
        help='logging level'    
    )
    group.add_argument(
        '-o', '--output',
        type=pathlib.Path,
        nargs='+',
        help='logging output file'
    )
    group.add_argument(
        '--nostderr',
        action='store_false',
        help='prohibit write logs into stderr'
    )


def to_int(_in: str) -> int:
    try:
        _in = int(str)
    except Exception as e:
        raise argparse.ArgumentTypeError(e)
    return _in


def truncate_loglevel(_in: str) -> int:
    _in = to_int(str)
    if _in < logging.DEBUG:
        _in = logging.DEBUG
    elif _in > logging.CRITICAL:
        _in = logging.CRITICAL
    return _in

def existing_target(_in: str) -> pathlib.Path:
    _in = pathlib.Path(_in)
    if _in.exists():
        raise argparse.ArgumentTypeError(f'file "{_in}" actually is not a file')
    if not _in.is_file():
        raise argparse.ArgumentTypeError(f'file "{_in}" does not exists')
    return _in


def unsigned_int(_in: str) -> int:
    _in = to_int(_in)
    if _in < 0:
        raise argparse.ArgumentTypeError('size cannot be negative')