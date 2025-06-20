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


_logger = logging.getLogger(__file__)


def purge(file_path: pathlib.Path) -> None:
    """purge(file_path)
    Очищает указанный файл, если файла не существует
    вызывает FileNotFoundError, если существует, но
    не является файлом, то вызывается TypeError. То же
    исключение вызывается, если файл является симлинком
    """
    if not file_path.exists():
        msg = f'file "{file_path}" not found'
        _logger.error(msg)
        raise FileNotFoundError(msg)
    
    if not file_path.is_file():
        msg = f'"{file_path}" is not a file'
        _logger.error(msg)
        raise TypeError(msg)

    if file_path.is_symlink():
        msg = f'"{file_path}" is a symlink'
        _logger.error(msg)
        raise TypeError(msg)

    try:
        # Да-да, просто записываем 0 байт
        file_path.write_bytes(b'')
        _logger.info(f'file "{file_path}" purged')

    except PermissionError as pe:
        _logger.error(f'cannot purge "{file_path}": {pe}')
        raise pe

    except OSError as ose:
        _logger.error(f'cannot purge "{file_path}": {ose}')
        raise ose

    except Exception as e:
        _logger.error(f'cannot purge "{file_path}": {e}')
        raise e