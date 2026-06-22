from typing import Optional, Union, Any

from DataModelDict import DataModelDict as DM

import numpy as np

from ..query import load_query
from . import Value

class MonthValue(Value):
    """Variation of IntValue focused purely on months.  Note model uses xsd:gMonth format"""
    
    @property
    def style(self) -> str:
        """str: The value style"""
        return 'month'
    
    @staticmethod
    def str_to_number(val: str):
        """
        Convert a str version of the month to an integer version
        """
        converter = {
            # Short month names
            'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6,
            'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12, 'sept':9,

            # Long month names
            'january':1, 'february':2, 'march':3, 'april':4, 'may':5, 'june':6,
            'july':7, 'august':8, 'september':9, 'october':10, 'november':11, 'december':12,
        }

        # Convert xsd:gMonth str format to Month
        if val[:2] == '--':
            return int(val[2:4])
        
        # Convert string
        elif val.lower() in converter:
            return converter[val.lower()]
        
        else:
            return int(val)
        
    @property
    def fullname(self) -> str:
        """str: The full month name"""
        if self.value is None:
            return None
        
        converter = {
            1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June',
            7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'
        }
        return converter[self.value]
    
    @property
    def shortname(self) -> str:
        """str: The 3 letter short name for the month"""
        if self.value is None:
            return None
        
        converter = {
            1:'jan', 2:'feb', 3:'mar', 4:'apr', 5:'may', 6:'jun',
            7:'jul', 8:'aug', 9:'sep', 10:'oct', 11:'nov', 12:'dec'
        }
        return converter[self.value]
    
    @property
    def xsd_gmonth(self) -> str:
        """str: the xsd:gMonth format of the month"""
        if self.value is None:
            return None
        
        return f'--{self.value:02}'

    def set_value_mod(self, val):

        # Check if value is in #text
        val = self.set_value_mod_textfield(val)

        if val is None:
            return None
        
        if isinstance(val, float):
            rval = round(val)
            if not np.isclose(rval, val):
                raise TypeError(f'{self.name} not an int!')
            val = rval
        
        elif isinstance(val, str):
            val = self.str_to_number(val)
        
        elif not isinstance(val, int):
            raise TypeError('unsupported type for month value')
        
        if val < 1 or val > 12:
            raise ValueError('month value must range from 1 to 12')
        
        return val
    
    def build_model_value(self):
        """Function to modify how values are represented in the model"""
        return self.xsd_gmonth

    @property
    def _default_queries(self) -> dict:
        """dict: Default query operations to associate with the Parameter style"""
        if self.metadatakey is False:
            return {}
        else:
            return {
                self.name: load_query('month_match',
                                    name=self.metadatakey,
                                    parent=self.metadataparent,
                                    path=f'{self.record.modelroot}.{self.modelpath}',
                                    description=f'Return only the records where {self.description} matches a given month integer value')
            }