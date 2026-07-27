
# Standard Python libraries
from typing import Any, Optional

import pandas as pd

# Relative imports
from ..tools import aslist, iaslist
from .Query import Query

class StrMatchQuery(Query):
    """Class for querying str fields for specific values"""

    @property
    def style(self) -> str:
        """str: The query style"""
        return 'str_match'

    @property
    def parameter_type(self) -> str:
        """str: The types of query parameter values accepted by this query style"""
        return 'str or list, optional'

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
        # Get path and add prefix
        path = f'{prefix}{self.path}'

        if value is not None:

            # Build the query 
            querylist.append( {path: {'$in': aslist(value)} } )

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

        def apply_function(series: pd.Series,
                           name: str,
                           value: Any,
                           parent: Optional[str]) -> bool:
            """
            function for pandas.DataFrame.apply with axis=1
            
            Parameters
            ----------
            series : pd.Series
                A series of the DataFrame being operated on.
            name : str
                The element name.
            value : any
                The values to search for.
            parent : str or None
                The parent element name, if there is one.

            Returns
            -------
            bool
                True if value is None or if one given value matches the
                element being checked.
            """
            # Return True for all fields if value is None
            if value is None:
                return True
            
            if parent is None:
                
                # Check if name is in series
                if name not in series or pd.isna(series[name]):
                    return False

                # Check for a value match
                return series[name] in aslist(value)
            
            else:

                 # Loop over all child elements
                for child in iaslist(series[parent]):

                    # Check if child element has name
                    if name in child and pd.notna(child[name]):
                        
                        # Check if child element matches a value
                        if child[name] in aslist(value):
                            return True
                
                # Return default False for no matching child elements
                return False

        # Use apply_function on df using value and object attributes
        return df.apply(apply_function, axis=1, args=(self.name, value, self.parent)).astype(bool)
