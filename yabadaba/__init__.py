from importlib.metadata import version
__version__ = version('yabadaba')

# Relative imports
from . import typing

from .UnitConverter import unitconvert
from . import tools
from .Settings import settings

from . import query
from .query import querymanager, load_query

from . import value
from .value import valuemanager, load_value

from . import record
from .record import recordmanager, load_record

from . import database
from .database import databasemanager, load_database

from .check_modules import check_modules
from .querydoc import querydoc
from .valuedoc import valuedoc

__all__ = ['__version__', 'typing', 'tools', 'settings', 'unitconvert',
           'query', 'load_query', 'querymanager',
           'record', 'load_record', 'recordmanager',
           'value', 'load_value', 'valuemanager',
           'database', 'load_database', 'databasemanager',
           'check_modules', 'querydoc', 'valuedoc']
__all__.sort()
