from datetime import datetime, timedelta
import plotly.figure_factory as ff

class Utils(object):

    @classmethod
    def dateTransform(cls, today, values):
        '''
        int to datetime
        '''
        return [(today + timedelta(days=delta)).strftime('%Y-%m-%d') for delta in values]

    @classmethod
    def value_to_date(cls, today, values):
        '''
        int to datetime
        '''
        return [(today + timedelta(days=delta)) for delta in values]
