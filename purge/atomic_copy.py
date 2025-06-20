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


import shutil
import tempfile
import pathlib
import logging
import os


_logger = logging.getLogger(__file__)

DEFAULT_CHUNK = 1024 * 8


def atomic_copy(src: pathlib.Path, dst: pathlib.Path, chunk: int = DEFAULT_CHUNK) -> bool:
    success = True
    tmp_path = None

    # Проверка места на диске
    try:
        mem_required  = src.stat().st_size
        mem_available = shutil.disk_usage(dst.parent).free
        _logger.debug(f'memory required: {mem_required}, memory available: {mem_available}')

    except OSError as ose:
        _logger.error(f'cannot check available memory: {ose}')
        return False        

    if mem_available < mem_required:
        _logger.error(f'not enough memory for copying "{src}" to "{dst}"')
        return False

    try:
        # Создаём промежуточный временный файл
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.tmp',
            dir=dst.parent,
            delete=False
        ) as tmpf:
            tmp_path = pathlib.Path(tmpf.name)
            _logger.debug(f'created temporary file: "{tmpf.name}"')
            
            # Записываем частами, чтобы не перенагружать память,
            # если будет большой файл
            with open(src, mode='rb') as srcf:
                while True:
                    data = srcf.read(chunk)
                    if not data:
                        break
                    tmpf.write(data)
                    _logger.debug(f'wrote {len(data)} bytes')
            
        # Теперь переносим всю необходимую инфу о файле
        shutil.copymode(src, tmp_path)
        shutil.copystat(src, tmp_path)

        # А теперь стараемся переименовать файл, чтоб сымитировать
        # атомарное копирование
        os.replace(tmp_path, dst)            

    except PermissionError as pe:
        _logger.error(f'copying to "{dst}" failed: permission denied: {pe}')
        success = False

    except OSError as ose:
        _logger.error(f'copying to "{dst}" failed: I/O error: {ose}')
        success = False

    except Exception as e:
        _logger.error(f'copying to "{dst}" failed: unexpected error: {e}')
        success = False

    finally:
        
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
                _logger.debug('removed temporary file')
            except Exception as e:
                _logger.error(f'cannot remove temporary file: {e}')

    if success:
        _logger.info(f'"{src}" copied to "{dst}"')

    return success
