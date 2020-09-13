class Filter(object):
    """Filter object applies to ship objects to limit display on app"""
    @classmethod
    def by_value(cls, df, values, functions, columns):
        index = True
        for value, func, column in zip(values, functions, columns):
            index &= getattr(cls, func)(df, value, column)
        return index

    @classmethod
    def by_date(cls, df, dates, column='date'):
        '''
        return index [True, True, False....]
        '''
        return (getattr(df, column) <= dates[1]) & (getattr(df, column) >= dates[0])

    @classmethod
    def by_name(cls, df, names: list, column='name'):
        '''
        return index [True, True, False....]
        '''
        return (getattr(df, column).isin(names))

    @classmethod
    def by_country(cls, df, countries: list, column='country'):
        '''
        return index [True, True, False....]
        '''
        return (getattr(df, column).isin(countries))
    

    @classmethod
    def by_longitude(cls, df, longitudes: list, column='longitude'):
        return  (getattr(df, column) <= longitudes[1]) & (getattr(df, column) >= longitudes[0])


    @classmethod
    def by_latitude(cls, df, latitudes: list, column='latitude'):
        return  (getattr(df, column) <= latitudes[1]) & (getattr(df, column) >= latitudes[0])