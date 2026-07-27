
from yabadaba import load_query

from test_Query import BaseTestQuery
import pandas as pd

class TestFloatMatchQuery(BaseTestQuery):

    @property
    def style(self) -> str:
        return 'float_match'

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
        query.mongo(querylist, 57)
        querydict = querylist[0]
        assert querydict['$or'][0]['root.element']['$gte'] == 56.99999
        assert querydict['$or'][0]['root.element']['$lte'] == 57.00001

        # Check multiple values
        querylist = []
        query.mongo(querylist, [105, '95'])
        querydict = querylist[0]
        assert querydict['$or'][0]['root.element']['$gte'] == 104.99999
        assert querydict['$or'][0]['root.element']['$lte'] == 105.00001
        assert querydict['$or'][1]['root.element']['$gte'] == 94.99999
        assert querydict['$or'][1]['root.element']['$lte'] == 95.00001

        # Check single value with prefix
        querylist = []
        query.mongo(querylist, 57, prefix='content.')
        querydict = querylist[0]
        assert querydict['$or'][0]['content.root.element']['$gte'] == 56.99999
        assert querydict['$or'][0]['content.root.element']['$lte'] == 57.00001

    @property
    def df(self) -> pd.DataFrame:
        """pd.Dataframe: demo data for filter testing"""

        return pd.DataFrame([
            {
                'name': 'first',
                'thisguy': 57,
                'parent': [
                    {
                        'thisguy': 7
                    },
                    {
                        'thisguy': 80
                    }
                ],
            },
            {
                'name': 'second',
                'thisguy': '95',
                'parent': [
                    {
                        'thisguy': '12'
                    },
                    {
                        'thisguy': '-8'
                    }
                ],
            },
            {
                'name': 'third',
                'thisguy': 105,
                'parent': [
                    {
                        'thisguy': 50
                    },
                    {
                        'thisguy': 6785
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
        df2 = df[query.pandas(df, 0)]
        assert len(df2) == 0

        # Test single value
        df2 = df[query.pandas(df, 57)]
        assert len(df2) == 1
        assert df2.name.tolist()[0] == 'first'

        # Test multiple values
        df2 = df[query.pandas(df, [95, '105'])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'second'
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
        df2 = df[query.pandas(df, 0)]
        assert len(df2) == 0

        # Test single value
        df2 = df[query.pandas(df, -8)]
        assert len(df2) == 1
        assert df2.name.tolist()[0] == 'second'

        # Test multiple values
        df2 = df[query.pandas(df, [7, '50'])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'first'
        assert df2.name.tolist()[1] == 'third'

    def test_inline(self):
        """This tests the old non-class version of the queries"""

        # Test mongo
        querylist = []
        load_query('float_match', path='root.element').mongo(querylist, [105, '95'])
        querydict = querylist[0]
        assert querydict['$or'][0]['root.element']['$gte'] == 104.99999
        assert querydict['$or'][0]['root.element']['$lte'] == 105.00001
        assert querydict['$or'][1]['root.element']['$gte'] == 94.99999
        assert querydict['$or'][1]['root.element']['$lte'] == 95.00001

        # Test pandas
        df = self.df
        df2 = df[load_query('float_match', name='thisguy', parent='parent').pandas(df, [7, '50'])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'first'
        assert df2.name.tolist()[1] == 'third'
