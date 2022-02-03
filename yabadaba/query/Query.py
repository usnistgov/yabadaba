# coding: utf-8

class Query():
    """
    Base Query class.  Each Query class defines a query operation and each
    Query object is associated with a specific data field.
    """
    
    def __init__(self, name=None, parent=None, path=None):
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
        """
        # Check that object is a subclass
        if self.__module__ == __name__:
            raise TypeError("Don't use Database itself, only use derived classes")

        self.name = name
        self.parent = parent
        self.path = path

    @property
    def style(self):
        """str: The query style"""
        raise NotImplementedError('Not defined for base class')

    @property
    def name(self):
        """str: The metadata key associated with the data field"""
        if self.__name is None:
            raise AttributeError('name not set')
        return self.__name

    @name.setter
    def name(self, value):
        if value is None:
            self.__name = None
        elif isinstance(value, str):
            self.__name = value
        else:
            raise TypeError('name must be None or a string')

    @property
    def parent(self):
        """str or None: The parent metadata key, if any."""
        return self.__parent

    @parent.setter
    def parent(self, value):
        if value is None:
            self.__parent = None
        elif isinstance(value, str):
            self.__parent = value
        else:
            raise TypeError('parent must be None or a string')

    @property
    def path(self):
        """str: The period delimited path to the associated field."""
        if self.__path is None:
            raise AttributeError('path not set')
        return self.__path

    @path.setter
    def path(self, value):
        if value is None:
            self.__path = None
        elif isinstance(value, str):
            self.__path = value
        else:
            raise TypeError('path must be None or a string')

    @property
    def description(self):
        """str: Describes the query operation that the class performs."""
        raise NotImplementedError('Not defined for base class')

    def mongo(self, querydict, value):
        """
        Builds a Mongo query operation for the field.

        Parameters
        ----------
        querydict : dict
            The set of mongo query operations that the new operation will be
            added to.
        value : any
            The value of the field to query on.  If None, then no new query
            operation will be added.
        """
        # Do nothing - base class
        pass

    def pandas(self, df, value):
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
        return df.apply(lambda series:True, axis=1)