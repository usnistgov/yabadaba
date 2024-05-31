from typing import Optional, Union, Any

from DataModelDict import DataModelDict as DM

from ..query import load_query
from . import Value

class StrValue(Value):
    
    def set_value_mod(self, val):
        if val is None:
            return None
        else:
            return str(val)
    
    @property
    def _default_queries(self) -> dict:
        """dict: Default query operations to associate with the Parameter style"""
        return {
            self.name: load_query('str_match',
                                  name=self.metadatakey,
                                  parent=self.metadataparent,
                                  path=f'{self.record.modelroot}.{self.modelpath}',
                                  description=f'Return only the records where {self.name} matches a given value')
        }