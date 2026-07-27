
# Standard Python libraries
from typing import Any, Optional

import pandas as pd
class Query():
    """
    Base Query class.  Each Query class defines a query operation and each
    Query object is associated with a specific data field.
    """
    
    def __init__(self,
                 name: Optional[str] = None,
                 parent: Optional[str] = None,
                 path: Optional[str] = None,
                 description: str = ''):
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
        """
        # Check that object is a subclass
        if self.__module__ == __name__:
            raise TypeError("Don't use Query itself, only use derived classes")

        self.name = name
        self.parent = parent
        self.path = path
        self.description = description

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            The string representation of the query.
        """
        return f'query style {self.style}'

    @property
    def style(self) -> str:
        """str: The query style"""
        raise NotImplementedError('Not defined for base class')

    @property
    def parameter_type(self) -> str:
        """str: The types of query parameter values accepted by this query style"""
        return 'str or list, optional'

    @property
    def name(self) -> str:
        """str: The metadata key associated with the data field"""
        if self.__name is None:
            raise AttributeError('name not set')
        return self.__name

    @name.setter
    def name(self, value: Optional[str]):
        if value is None:
            self.__name = None
        elif isinstance(value, str):
            self.__name = value
        else:
            raise TypeError('name must be None or a string')

    @property
    def parent(self) -> Optional[str]:
        """str or None: The parent metadata key, if any."""
        return self.__parent

    @parent.setter
    def parent(self, value: Optional[str]):
        if value is None:
            self.__parent = None
        elif isinstance(value, str):
            self.__parent = value
        else:
            raise TypeError('parent must be None or a string')

    @property
    def path(self) -> str:
        """str: The period delimited path to the associated field."""
        if self.__path is None:
            raise AttributeError('path not set')
        return self.__path

    @path.setter
    def path(self, value: Optional[str]):
        if value is None:
            self.__path = None
        elif isinstance(value, str):
            self.__path = value
        else:
            raise TypeError('path must be None or a string')

    @property
    def description(self) -> str:
        """str: Describes the query operation"""
        return self.__description
    
    @description.setter
    def description(self, value: str):
        self.__description = str(value)

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
        # Do nothing - base class
        pass

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
        # Do nothing - base class
        return df.apply(lambda series:True, axis=1).astype(bool)
