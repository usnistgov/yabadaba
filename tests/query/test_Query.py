
# https://docs.pytest.org/en/latest/
from pytest import raises

import pandas as pd

import yabadaba
from yabadaba import load_query, querymanager

def test_Query():
    """Tests that the base Query class cannot be loaded"""

    with raises(TypeError):
        yabadaba.query.Query('test')

def test_querymanager():
    assert len(querymanager.loaded_style_names) > 0

class BaseTestQuery():
    """
    A template class for testing Query subclasses
    """

    @property
    def style(self) -> str:
        raise NotImplementedError('needs to be defined for subclass')
    
    def test_default(self):
        """Test default loading."""

        assert self.style in querymanager.loaded_style_names
        query = load_query(self.style)
        assert query.style == self.style
        assert isinstance(query.description, str)

    def test_mongo_no_path(self):
        """Tests mongo query without required path"""
        
        # Load query with no parameters
        query = load_query(self.style)

        # Test unset path
        with raises(AttributeError):
            query.path

        # Test mongo with unset path
        querydict = {}
        with raises(AttributeError):
            query.mongo(querydict, None)

        # Test setting path directly
        query.path = None
        query.path = 'root.element'
        assert query.path == 'root.element'

    def test_mongo(self):
        """Tests mongo query"""
        raise NotImplementedError('needs to be defined for subclass')

    @property
    def df(self) -> pd.DataFrame:
        """pd.Dataframe: demo data for filter testing"""
        raise NotImplementedError('needs to be defined for subclass')

    def test_pandas_no_name(self):
        """Tests pandas filter without required name"""
        
        df = self.df

        # Load query with no parameters
        query = load_query(self.style)

        # Test no name
        with raises(AttributeError):
            query.name

        # Test pandas with no name
        with raises(AttributeError):
            df2 = query.pandas(df, None)

         # Test setting name directly
        query.name = None
        query.name = 'thisguy'
        assert query.name == 'thisguy'

    def test_pandas(self):
        """Tests pandas filter without a parent element"""
        raise NotImplementedError('needs to be defined for subclass')

    def test_pandas_parent(self):
        """Tests pandas filter with a parent element"""
        raise NotImplementedError('needs to be defined for subclass')

    def test_inline(self):
        """This tests the old non-class version of the queries"""
        raise NotImplementedError('needs to be defined for subclass')