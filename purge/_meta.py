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

"""purge
Простая программа для ротации логов. Проверяет целефой файл
на соответствие размерам, указанных пользователем, и очищает
его, предварительно создавая копию, если не указан флаг -n | --nocopy.


"""


PACKAGE_NAME = 'Purge'

PACKAGE_VERSION = 'v0.1.0'

SHORT_DESCRIPTION = 'a simple log rotation util'
LONG_DESCRIPTION = '''a simple log totation util that allows to
create backups for files, put backups in archives and remove them
when they get too old to be useful =)'''


UNITS = {
    'B' : 1 ,
    'KB': 2 ** 10,
    'MB': 2 ** 20,
    'GB': 2 ** 30 
}
DEFAULT_UNIT = 'KB'