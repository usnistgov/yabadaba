from datetime import date

from yabadaba import load_query

from test_Query import BaseTestQuery
import pandas as pd

class TestDateMatchQuery(BaseTestQuery):

    @property
    def style(self) -> str:
        return 'date_match'

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
        query.mongo(querylist, date(2017, 2, 16))
        querydict = querylist[0]
        assert querydict['root.element']['$in'] == ['2017-02-16']

        # Check multiple values
        querylist = []
        query.mongo(querylist, [date(2017, 2, 16), date(2019, 7, 28)])
        querydict = querylist[0]
        assert querydict['root.element']['$in'] == ['2017-02-16', '2019-07-28']

        # Check single value with prefix
        querylist = []
        query.mongo(querylist, date(2017, 2, 16), prefix='content.')
        querydict = querylist[0]
        assert querydict['content.root.element']['$in'] == ['2017-02-16']

    @property
    def df(self) -> pd.DataFrame:
        """pd.Dataframe: demo data for filter testing"""

        return pd.DataFrame([
            {
                'name': 'first',
                'thisguy': '2017-02-16',
                'parent': [
                    {
                        'thisguy': '1989-11-05'
                    },
                    {
                        'thisguy': '1999-10-25'
                    }
                ],
            },
            {
                'name': 'second',
                'thisguy': '2019-07-28',
                'parent': [
                    {
                        'thisguy': '2015-07-05'
                    },
                    {
                        'thisguy': '2010-01-01'
                    }
                ],
            },
            {
                'name': 'third',
                'thisguy': '2016-17-02',
                'parent': [
                    {
                        'thisguy': '1957-03-21'
                    },
                    {
                        'thisguy': '1875-02-07'
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
        df2 = df[query.pandas(df, date(1900, 1, 1))]
        assert len(df2) == 0

        # Test single value
        df2 = df[query.pandas(df, date(2017, 2, 16))]
        assert len(df2) == 1
        assert df2.name.tolist()[0] == 'first'

        # Test multiple values
        df2 = df[query.pandas(df, [date(2017, 2, 16), date(2019, 7, 28)])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'first'
        assert df2.name.tolist()[1] == 'second'

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
        df2 = df[query.pandas(df, date(1900, 1, 1))]
        assert len(df2) == 0

        # Test single value
        df2 = df[query.pandas(df, date(2015, 7, 5))]
        assert len(df2) == 1
        assert df2.name.tolist()[0] == 'second'

        # Test multiple values
        df2 = df[query.pandas(df, [date(2015, 7, 5), date(1875, 2, 7)])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'second'
        assert df2.name.tolist()[1] == 'third'

    def test_inline(self):
        """This tests the old non-class version of the queries"""

        # Test mongo
        querylist = []
        load_query('date_match', path='root.element').mongo(querylist, [date(2017, 2, 16), date(2019, 7, 28)])
        querydict = querylist[0]
        assert querydict['root.element']['$in'] == ['2017-02-16', '2019-07-28']
        
        # Test pandas
        df = self.df
        df2 = df[load_query('date_match', name='thisguy', parent='parent').pandas(df, [date(2015, 7, 5), date(1875, 2, 7)])]
        assert len(df2) == 2
        assert df2.name.tolist()[0] == 'second'
        assert df2.name.tolist()[1] == 'third'
