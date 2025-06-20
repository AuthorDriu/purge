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


import logging
import logging.handlers
import pathlib
import copy
import sys        


_INNER_LOGGER_MAX_BYTES         = 1024 * 5
_INNER_LOGGER_BACKUPS_COUNT     = 10


class MultilineFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        if '\n' in message:
            # Добавляем отступ для всех строк после первой
            header, *lines = message.splitlines()
            formatted_lines = [header] + [f'| {line}' for line in lines]
            return '\n'.join(formatted_lines)
        return message


def setup_logger(
        loglevel: int,
        logfiles: list[pathlib.Path],
        handlers: list[logging.Handler],
        
        format:   str  = "[%(asctime)s] %(message)s",
        nostderr: bool = False,
) -> None:
    """setup_logger()
    initializes the global logger with provided logging level,
    log files and handlers
    """

    errors = []
    def e(message: str) -> None:
        errors.append(message)


    # Чтобы случайно не изменить на всякий случай скопирую всё, что можно изменить извне
    _logfiles = copy.deepcopy(logfiles)
    _handlers = copy.copy(handlers)

    # Добавить вывод в stderr, если разрешено
    if not nostderr:
        _handlers.append(logging.StreamHandler(stream=sys.stderr))

    # Добавить внутренний логгер
    inner_logger_dir = pathlib.Path(__file__).parent.parent / 'logs'

    if not inner_logger_dir.is_dir():
        # Если logs/ не является директорией, но при этом существует, то это конфликт :_)
        if inner_logger_dir.exists():
            raise FileExistsError(f'"{inner_logger_dir}" already exists and is\'s not a directory')
        inner_logger_dir.mkdir()

    inner_logger_path = inner_logger_dir / 'purge.log'
    inner_logger = logging.handlers.RotatingFileHandler(
        inner_logger_path,
        maxBytes=_INNER_LOGGER_MAX_BYTES,
        backupCount=_INNER_LOGGER_BACKUPS_COUNT
    )
    inner_logger.setLevel(logging.WARNING)
    _handlers.append(inner_logger)

    # Добавить файлы к списку обработчиков
    for pathfile in _logfiles:
        error_base = f'cannot initialize logging file handler for "{pathfile}": '
        
        try:
            _handlers.append(logging.FileHandler(pathfile))

        except PermissionError:
            e(error_base + 'permission denied')
        except OSError as ose:
            e(error_base + f'I/O error: {ose}')
        except Exception as e:
            e(error_base + f'unexpected error: {e}')

    for h in _handlers:
        h.setFormatter(MultilineFormatter())

    logging.basicConfig(
        level=loglevel,
        format=format,
        handlers=_handlers
    )
    _show_parameters(loglevel, logfiles, handlers, nostderr)
    
    if len(errors) > 0:
        report = '\n'.join(errors)
        logging.error(report)


def _show_parameters(
        loglevel: int,
        logfiles: list[pathlib.Path],
        handlers: list[logging.Handler],
        nostderr: bool
) -> None:
    """_show_parameters()
    just prints logging parameters in debug
    """
    # Просто пропускаем, если сообщение всё равно не выведется
    # зачем время тратить на создание строки с отчётом?)
    if loglevel > logging.DEBUG:
        return

    # У DeepSeek украл способ более приятного способа формирования отчёта
    # До этого я делал всё через строку и локальную функцию 
    # def _(line, indent):
    #     global report
    #     report += '\n' + ('    ' * indent) + line
    #
    # Честно, не успел проверить работает она ли вообще
    lines = ['LOGGING PARAMETERS REPORT:']

    def _(line: str, indent: int = 0) -> None:
        lines.append(('    ' * indent) + line)

    _(f'NOSTDERR: ' + ('yes' if nostderr else 'no'))

    _('LOGFILES:')
    if len(logfiles) > 0:
        for filepath in logfiles:
            _(str(filepath), 1)
    else:
        _('[NOTHING]', 1)
    
    _('HANDLERS:')
    for h in handlers:
        _(repr(h), 1)
    
    report = '\n'.join(lines)
    logging.debug(report)