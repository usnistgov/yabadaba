
# iprPy imports
from . import recordmanager, databasemanager, querymanager, valuemanager

__all__ = ['check_modules']

def check_modules():
    """
    Prints lists of the modular components that were successfully and
    unsuccessfully loaded.
    """
    databasemanager.check_styles()
    print()
    recordmanager.check_styles()
    print()
    querymanager.check_styles()
    print()
    valuemanager.check_styles()
    print()

