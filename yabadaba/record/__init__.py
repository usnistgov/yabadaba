__all__ = ['Record', 'recordmanager', 'load_record']

# Standard Python libraries
from typing import Optional, Union

from DataModelDict import DataModelDict as DM

# Relative imports
from .. import valuemanager
from .Record import Record
from ..tools import ModuleManager

# Initialize ModuleManager for records
recordmanager = ModuleManager('Record')

# Define load_record
def load_record(style: str,
                model: Union[str, DM, None] = None,
                name: Optional[str] = None,
                database = None,
                **kwargs) -> Record:
    """
    Loads a Record subclass associated with a given record style.

    Parameters
    ----------
    style : str
        The record style.
    name : str, optional
        The name to give to the specific record.
    model : str, DataModelDict, optional
        Data model content to load for the given record style.
    database : yabadaba.Database, optional
        Allows for a default database to be associated with the record.
    **kwargs : any
        Any extra keyword parameter supported by the record style.

    Returns
    -------
    subclass of Record 
        A Record object for the style
    """
    record = recordmanager.init(style, model=model, name=name, **kwargs)
    if database is not None:
        record.database = database
    return record


# Append Record Values to valuemanager
valuemanager.import_style('record', '.RecordListValue', __name__)
valuemanager.import_style('recordlist', '.RecordListValue', __name__)
valuemanager.import_style('recordsubset', '.RecordSubsetValue', __name__)


