
from yabadaba import load_query

from test_Query import BaseTestQuery
import pandas as pd

class TestStrMatchQuery(BaseTestQuery):

    @property
    def style(self) -> str:
        return 'str_match'

    def test_mongo(self):
        """Tests mongo query"""

        # Test setting path when loading
        query = load_query(self.style, path='root.element')
        assert query.path == 'root.element'

        # Test None value
        querylist = []
        query.mongo(querylist, None)
        assert len(querylist) == 0

        # Check single value
        querylist = []
        query.mongo(querylist, 'value')
        querydict = querylist[0]
        assert querydict['root.element']['$in'] == ['value']

        # Check multiple values
        querylist = []
        query.mongo(querylist, ['value1', 'value2'])
        querydict = querylist[0]
        assert querydict['root.element']['$in'] == ['value1', 'value2']

        # Check single value with prefix
        querylist = []
        query.mongo(querylist, 'value', prefix='content.')
        querydict = querylist[0]
        assert querydict['content.root.element']['$in'] == ['value']

    @property
    def df(self) -> pd.DataFrame:
        """pd.Dataframe: demo data for filter testing"""

        return pd.DataFrame([
            {
                'name': 'first',
                'thisguy': 'field contains value1',
                'parent': [
                    {
                        'thisguy': 'child field'
                    },
                    {
                        'thisguy': 'child field'
                    }
                ],
            },
            {
                'name': 'second',
                'thisguy': 'field contains value1 and value2',
                'parent': [
                    {
                        'thisguy': 'child field with value1'
                    },
                    {
                        'thisguy': 'child field with value2'
                    }
                ],
            },
            {
                'name': 'third',
                'thisguy': 'field',
                'parent': [
                    {
                        'thisguy': 'child field'
                    },
                    {
                        'thisguy': 'child field with value1 and value2'
                    }
                ],
            },
        ])

    def test_pandas(self):
        """Tests pandas filter without a parent element"""

        df = self.df

        # Test setting path when loading
        query = load_query(self.style, name='thisguy')
        assert query.name == 'thisguy'

        # Test None value
        df2 = df[query.pandas(df, None)]
        assert len(df2) == 3

        # Test single missing value
        df2 = df[query.pandas(df, 'NOT THERE')]
        assert len(df2) == 0

        # Test single value
        df2 = df[query.pandas(df, 'field')]
        assert len(df2) == 1
        assert df2.name.tolist()[0] == 'third'

        # Test multiple values
        df2 = df[query.pandas(df, ['field', 'field contains value1'])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'first'
        assert df2.name.tolist()[1] == 'third'

    def test_pandas_parent(self):
        """Tests pandas filter with a parent element"""

        df = self.df

        # Test setting parent when loading
        query = load_query(self.style, name='thisguy', parent='parent')
        assert query.name == 'thisguy'
        assert query.parent == 'parent'

        # Test directly setting parent
        query.parent = None
        assert query.parent is None
        query.parent = 'parent'
        assert query.parent == 'parent'

        # Test None value
        df2 = df[query.pandas(df, None)]
        assert len(df2) == 3

        # Test single missing value
        df2 = df[query.pandas(df, 'NOT THERE')]
        assert len(df2) == 0

        # Test single value
        df2 = df[query.pandas(df, 'child field')]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'first'
        assert df2.name.tolist()[1] == 'third'

        # Test multiple values
        df2 = df[query.pandas(df, ['child field with value1', 'child field with value1 and value2'])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'second'
        assert df2.name.tolist()[1] == 'third'

    def test_inline(self):
        """This tests the old non-class version of the queries"""

        # Test mongo
        querylist = []
        load_query('str_match', path='root.element').mongo(querylist, ['value1', 'value2'])
        querydict = querylist[0]
        assert querydict['root.element']['$in'] == ['value1', 'value2']

        # Test pandas
        df = self.df
        df2 = df[load_query('str_match', name='thisguy', parent='parent').pandas(df, ['child field with value1', 'child field with value1 and value2'])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'second'
        assert df2.name.tolist()[1] == 'third'
