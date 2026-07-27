# Standard Python libraries
from typing import Optional

# Relative imports
from ..tools import screen_input, ModuleManager
from . import databasemanager as default_databasemanager
from . import Database
from .. import settings as default_settings
from .. import Settings

__all__ = ['load_database']

def load_database(name: Optional[str] = None,
                  style: Optional[str] = None,
                  host: Optional[str] = None,
                  settings: Optional[Settings.Settings] = None, 
                  databasemanager: Optional[ModuleManager] = None,
                  **kwargs) -> Database:
    """
    Loads a database object.  Can be either loaded from stored settings or
    by defining all needed access information.
    
    Parameters
    ----------
    name : str, optional
        The name assigned to a pre-defined database.  If given, can be the only
        parameter.
    style : str, optional
        The database style to use.
    host : str, optional
        The URL/file path where the database is hosted.
    settings : yabadaba.Settings.Settings, optional
        A Settings object.  Allows for different settings files to be used
        by downstream packages.
    databasemanager : yabadaba.tools.ModuleManager, optional
        Allows for an alternate databasemanager to be specified by downstream
        packages. 
    kwargs : dict, optional
        Any other keyword parameters defining necessary access information.
        Allowed keywords are database style-specific.
    
    Returns
    -------
    Subclass of datamodelbase.Database
        The database object.
    """

    # Check that style and name are both not given
    if style is not None and name is not None:
        raise ValueError('name and style cannot both be given')

    # Set default package values 
    if settings is None:
        settings = default_settings
    if databasemanager is None:
        databasemanager = default_databasemanager

    # Load Database info from saved settings
    if style is None:

        if host is not None or len(kwargs) > 0:
            raise ValueError('style is required if host and/or kwargs are given')

        # Get information from settings file
        database_names = settings.list_databases
        
        # Ask for name if not given
        if name is None:
            if len(database_names) > 0:
                print('Select a database:')
                for i, database in enumerate(database_names):
                    print(i+1, database)
                choice = screen_input(':')
                try:
                    choice = int(choice)
                except ValueError:
                    name = choice
                else:
                    name = database_names[choice-1]
            else:
                raise KeyError('No databases currently set')
        
        try:
            kwargs = settings.databases[name]
        except KeyError as err:
            raise KeyError(f'database {name} not found') from err

        style = kwargs.pop('style')
        host = kwargs.pop('host')

    return databasemanager.init(style, host=host, **kwargs)
