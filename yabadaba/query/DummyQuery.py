
# Standard Python libraries
from typing import Any, Optional

import pandas as pd

# Relative imports
from ..tools import aslist

from .Query import Query

class DummyQuery(Query):
    """Class for a query field that doesn't perform a database query"""

    def __init__(self,
                 name: Optional[str] = None,
                 parent: Optional[str] = None,
                 path: Optional[str] = None,
                 description: str = '',
                 value: Optional[Any] = None):
        """
        Query initialization

        Parameters
        ----------
        name : str or None, optional
            The metadata key associated with the data field.  Must be set
            to use the pandas query method.
        parent : str or None, optional
            Allows for the pandas query operations to work on embedded
            metadata dicts.  If given, the pandas query method will check the
            value of metadata[parent][name].
        path : str or None, optional
            The record data path to the data field.  Levels are delimited by
            periods.  Must be given to use the mongo query method.
        description : str, optional
            Description of the query operation, i.e. what it is searching.
        value : any, optional
            If None (default), then the query operations will do nothing
            (i.e. always return True values). If a different value is
            given, then the value(s) provided during the query call will
            be checked against this value for a match to determine if all
            True or all False are returned by the query operation.
        """
        super().__init__(name, parent, path, description)
        self.__value = value

    @property
    def style(self) -> str:
        """str: The query style"""
        return 'dummy'

    @property
    def parameter_type(self) -> str:
        """str: The types of query parameter values accepted by this query style"""
        return 'any, optional'

    @property
    def value(self) -> Any:
        """Any: A single constant value that will always"""
        return self.__value
    
    def mongo(self,
              querylist: list,
              value: Any,
              prefix: str = ''):
        """
        Builds a Mongo query operation for the field.

        Parameters
        ----------
        querylist : list
            The working list of mongo query operations which is to be appended
            with the operation for this query object.
        value : any
            The value of the field to query on.  If None, then no new query
            operation will be added.
        prefix : str, optional
            An optional prefix to add before the query path.  Used by Record's
            mongoquery to start each path with "content."
        """
        # Build an always false query if self.value not in value
        if value is not None and self.value is not None:
            if self.value not in aslist(value):
                querylist.append( {'nonexistantpath': {'$exists': True} } )

    def pandas(self,
               df: pd.DataFrame,
               value: Any) -> pd.Series:
        """
        Applies a query filter to the metadata for the field.
        
        Parameters
        ----------
        df : pandas.DataFrame
            A table of metadata for multiple records of the record style.
        value : any
            The value of the field to query on.  If None, then it should return
            True for all rows of df.
        
        Returns
        -------
        pandas.Series
            Boolean map of matching values
        """
        # Construct all true values
        alltrue = pd.Series(True, df.index, dtype=bool)

        # Return all false if self.value not in value
        if value is not None and self.value is not None:        
            if self.value not in aslist(value):
                return ~alltrue

        # Otherwise return all true
        return alltrue
