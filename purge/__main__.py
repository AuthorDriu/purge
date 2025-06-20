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

import pathlib
import logging
import sys

from cli import parse_args
from logger import setup_logger
from atomic_copy import atomic_copy
from _purge import purge


_logger = None


def user_refuse():
    _logger.info('canceling the process by user\'s decition')
    sys.exit(0)


def confirm(msg: str) -> bool:
    """confirm(msg)
    использует stdout, чтобы запрос всегда отображался
    в терминале вне зависимости от выставленного уровня 
    логгирования.
    """
    expecting = {'yes': True, 'no': False}
    suffix    = ' [yes/no]: '
    answer    = ''

    while answer not in expecting:
        answer = input(msg+suffix).strip()
    
    return expecting[answer]


def generate_destination(src: pathlib.Path) -> pathlib.Path:
    """generate_destination(src)
    генерирует путь к файлу копии, название которого
    следует следующему формату: "<name>_copy<n>.<ext>",
    где:
        name - базовое название исходного файла
        n    - порядковый номер копии
        ext  - расширение исходного файла
    
    нумерация начинается с единицы
    """
    name = src.stem
    ext  = src.suffix
    n    = 1

    _ = lambda: pathlib.Path(f'{name}_copy{n}{ext}')
    dest = _()

    while dest.exists():
        n += 1
        dest = _()
    
    _logger.debug(f'generated destination path: "{dest}"')
    return dest


def main() -> None:
    global _logger

    args = parse_args()
    setup_logger(
        loglevel=args.level,
        logfiles=args.output,
        nostderr=args.nostderr,
        handlers=[],
    )
    _logger = logging.getLogger()

    src      = args.target
    min_size = args.size * args.units

    if src.stat().st_size < min_size:
        _logger.info('no actions required')
        sys.exit(0)
    
    dest = None

    if args.copy:
        dest = args.copy

    if not args.nocopy and not dest:
        if args.safe and not confirm(
            'destination file not specified. Generate?'
        ): user_refuse()
        dest = generate_destination(src)
    
    if dest:
        atomic_copy(src, dest)
    
    if not dest and not args.force:
        if not confirm(
            'purge "{src}" without copying may lead to loosing data. '
            'Are you sure?'
        ): user_refuse()
        else:
            _logger.warning(f'purging "{src}" without copying')
    
    try:
        purge(src)
    except Exception:
        # Логи уже есть в _purge.purge(), поэтому просто выхожу
        sys.exit(2)
    
    sys.exit(0)
        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass