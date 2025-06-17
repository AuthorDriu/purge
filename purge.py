#!/usr/bin/python3

"""purge.py
проверяет указанный файл на соответствие размерам и,
в случае, если он соответствует условию, копирует его
и очищает

пример использования:
    python pyrge.py syslog.log 10 -u KB -v -n

    если файл syslog.log больше или равен 10 килобайт (10240 байт) - удаляет его и подробно
    описывает весь процесс

обязательные аргументы:
    target          путь к целевому файлу
    size            размер файла, необходимый для дальнейшей работы скрипта

флаги:
    -u | --unit     единица измерения памяти. Возможные значения:
        B  - Байты     (по умолчанию    )
        KB - Килобайты (1024       байта)
        MB - Мегабайты (1048576    байт )
        GB - Гигабайты (1073741824 байта)
    
    -v | --verbose  подробный вывод
    -n | --nocopy   не копировать файл
    -o | --output   копировать файл по указанному пути

Если одновременно указаны флаги -n и -o копирование произойдет в указанный файл.
"""

import argparse
import pathlib
import logging
import shutil
import sys


TARGET_FILE_NOT_FOUND           = 1
TARGET_FILE_IS_A_DIR            = 2
TARGET_FILE_IS_A_SYMLINK        = 3
CANNOT_COPY                     = 4

UNITS = {
    'B':  1,
    'KB': 1024,
    'MB': 1048576,
    'GB': 1073741824
}


def parse_args() -> argparse.Namespace:
    """parse_args()
    Парсит аргументы командной строки и возвращает объект argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        pathlib.Path(__file__).name,
        usage='purge.py <target> <size> [options...]',
        description='purges and copies file if size of the file is greater than specified one'
    )
    parser.add_argument('target', type=pathlib.Path, help='target file')
    parser.add_argument('size', type=int, help='expected size of the file')
    parser.add_argument(
        '-u', '--unit',
        choices=('B', 'KB', 'MB', 'GB'),
        default='B',
        help='size unit'    
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='verbose mode'
    )
    parser.add_argument(
        '-n', '--nocopy',
        action='store_true',
        help='prohibit coping'
    )
    parser.add_argument(
        '-o', '--output',
        type=pathlib.Path,
        help='specifies the output file name' 
    )
    
    return parser.parse_args()


def setup_logger(verbosity: bool) -> None:
    """setup_logger()
    настраивает логгер
    """
    format = '%(message)s'
    level = logging.INFO if verbosity else logging.ERROR
    handlers = (
        logging.StreamHandler(stream=sys.stderr),
    )

    logging.basicConfig(
        format=format,
        level=level,
        handlers=handlers
    )


def convert_to_bytes(size: int, unit: str) -> int:
    """convert_to_bytes()
    конвертирует указанный размер из указанной единицы измерения
    в байты
    """
    return size * UNITS[unit]


def ask_rewrite_or_rename(destination: pathlib.Path) -> pathlib.Path | None:
    """ask_rewrite_or_rename()
    Спрашивает пользователя перезаписать ли файл
    или предлагает ввести новое название, после чего
    возвращает итоговый путь к файлу или ничто, если 
    необходимо завершить исполнение скрипта
    """

    ofile = destination
    options = ('yes', 'no')
    answer = ''

    while answer not in options:
        print(f'? file "{destination}" already exists. Rewrite? [yes/no]')
        answer = input('> ').strip()
    
    if answer == 'no':
        print('? enter new output file name or leave empty to cancel.')
        ofile = input('> ').strip()
        if ofile == '':
            return None        
        ofile = pathlib.Path(ofile)

    return ofile


def copy(target: pathlib.Path, destination: pathlib.Path) -> None:
    """copy_to()
    копирует файл по указанному пути, если подобный файл
    существует, спрашивает перезаписать ли, если нет,
    то спрашивает новое имя.

    Пример случая, если файл существует:
    python purge.py target.txt -o output.txt
    ? file "output.txt" already exists. Rewrite? [yes/no]
    > ss
    ? file "output.txt" already exists. Rewrite? [yes/no]
    > no
    ? enter new output file name or leave empty to cancel.
    > new_output.txt
    """

    if destination.exists():
        new_destination = ask_rewrite_or_rename(destination)

        if new_destination is None:
            logging.info('skip coping')
            return
        
        destination = new_destination
    
    try:
        shutil.copy(target, destination)
        logging.info(f'"{target}" copied to "{destination}"')

    except Exception as e:
        logging.error(f'cannot copy "{target}" to "{destination}": {e}')
        sys.exit(CANNOT_COPY)


def validate_target(target: pathlib.Path) -> None:
    """validate_target()
    проверяет не является ли целевой файл директорией или
    символьной ссылкой. В случае, если условия не проходят,
    программа завершается с сообщением об ошибке и с соответствующим
    кодом возврата.
    """

    if not target.exists():
        logging.error(f'"{target}" not exists ')
        sys.exit(TARGET_FILE_NOT_FOUND)
    elif target.is_dir():
        logging.error(f'"{target}" is a directory')
        sys.exit(TARGET_FILE_IS_A_DIR)
    elif target.is_symlink():
        logging.error(f'"{target}" is a symbolic link')
        sys.exit(TARGET_FILE_IS_A_SYMLINK)


def generate_destination_pathfile(target: pathlib.Path) -> pathlib.Path:
    """generate_destination_pathfile()
    генерирует путь к файлу, в которое должно будет произведено копирование

    алгоритм:
        1. название файла + _copy{n} + расширение файла, где n - номер файла копии. Отсчет
        начинается с единицы.
        2. если файл с таким названием существует, прибавляем к номеру единицу
    
    алгоритм повторяется пока не будет найден пустующий номер.
    """

    base = target.stem
    ext  = target.suffix
    n = 1
    gen_name = lambda: pathlib.Path(base + f'_copy{n}' + ext)

    destination = gen_name()
    while destination.exists():
        n += 1
        destination = gen_name()
    
    logging.info(f'generated destination path: {destination}')
    return destination


def main(
    target: pathlib.Path,
    size: int,
    unit: str,
    nocopy: bool,
    output: pathlib.Path | None
) -> None:
    
    validate_target(target)
    
    actual_size = target.stat().st_size
    expected_size = convert_to_bytes(size, unit)
    
    if actual_size < expected_size:
        logging.info('no actions required')
        sys.exit(0)
    
    destination = None
    if not nocopy or output is not None:
        if output is None:
            destination = generate_destination_pathfile(target)
        else:
            destination = output

        copy(target, destination)
    
    target.write_bytes(b'')
    logging.info(f'"{target}" purged')

    sys.exit(0)


if __name__ == '__main__':
    args = parse_args()
    setup_logger(verbosity=args.verbose)

    main(
        target=args.target,
        size=args.size,
        unit=args.unit,
        nocopy=args.nocopy,
        output=args.output
    )


