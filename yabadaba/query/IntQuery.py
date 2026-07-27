
# Standard Python libraries
from typing import Any, Optional

import numpy as np
import pandas as pd

# Relative imports
from ..tools import iaslist

from .Query import Query

class IntQuery(Query):
    """Class for querying int fields for matching values or ranges of values"""

    @property
    def style(self) -> str:
        """str: The query style"""
        return 'int'

    @property
    def parameter_type(self) -> str:
        """str: The types of query parameter values accepted by this query style"""
        return 'int, tuple or list, optional'

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
            
            # Handle unique case of a single 2-value tuple
            if isinstance(value, tuple) and len(value) == 2:
                value = [value]

            # Split values into single floats or tuples of (min, max)
            val = []
            valranges = []
            for v in iaslist(value):
                if isinstance(v, tuple) and len(v) == 2:
                    valranges.append(v)
                else:
                    val.append(int(v))

            # Init newquery as list of $or evaluations
            newquery = {'$or':[]}
            if len(val) > 0:
                newquery['$or'].append( {path: {'$in': val} } )
            
            for valrange in valranges:
                minval, maxval = self.range_check(valrange)
                newquery['$or'].append({path: {'$gte': minval, '$lte':maxval}})

            # Append newquery to querylist
            querylist.append(newquery)

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
            
            # Handle unique case of a single 2-value tuple
            if isinstance(value, tuple) and len(value) == 2:
                value = [value]

            # Split values into single floats or tuples of (min, max)
            val = []
            valranges = []
            for v in iaslist(value):
                if isinstance(v, tuple) and len(v) == 2:
                    valranges.append(v)
                else:
                    val.append(int(v))

            if parent is None:

                # Check if name is in series
                if name not in series or pd.isna(series[name]):
                    return False
                
                # Check for a direct value match
                if int(series[name]) in val:
                    return True
                
                # Check if value is in a given range
                for valrange in valranges:
                    minval, maxval = self.range_check(valrange)
                    if int(series[name]) >= minval and int(series[name]) <= maxval:
                        return True
                    
                # Return False for no matching values or ranges
                return False
            
            else:

                if parent not in series:
                    return False
                
                # Loop over all child elements
                for child in iaslist(series[parent]):

                    # Check if child element has name
                    if name in child and pd.notna(child[name]):

                        # Check if child element directly matches a value
                        if int(child[name]) in value:
                            return True
                        
                        # Check if value is in a given range
                        for valrange in valranges:
                            minval, maxval = self.range_check(valrange)
                            if int(child[name]) >= minval and int(child[name]) <= maxval:
                                return True

                # Return default False for no matching child elements
                return False

        # Use apply_function on df using value and object attributes
        return df.apply(apply_function, axis=1, args=(self.name, value, self.parent)).astype(bool)


    def range_check(self, valrange):
        """For range query values, numbers become int and None become +-inf"""
        if valrange[0] is not None:
            minval = int(valrange[0])
        else:
            minval = -np.inf

        if valrange[1] is not None:
            maxval = int(valrange[1])
        else:
            maxval = np.inf

        return (minval, maxval)