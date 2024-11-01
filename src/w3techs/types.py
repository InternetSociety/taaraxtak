# taaraxtak
# nick merrill
# 2021
#
# w3techs
# create-tables.py - defines the Postgres tables.
# (see file by the same name in repository's root).

from psycopg2.extensions import cursor
from psycopg2.extensions import connection
from typing import Optional
import src.shared.utils as shared_utils
import src.shared.types as shared_types

import pandas as pd

def is_float_0(my_float: float) -> bool:
    return (type(my_float) == float) & (my_float >= 0)

def is_float_0_1(my_float: float) -> bool:
    return (type(my_float) == float) & (my_float >= 0) & (my_float <= 1)

def is_float_0_3(my_float: float) -> bool:
    return (type(my_float) == float) & (my_float >= 0) & (my_float <= 3)

def validate_measurement_scope (s: str) -> bool:
    return (
        (s == 'all') or
        (s == 'top_10k') or
        (s == 'top_1k')
    )

class ProviderMarketshare():
    '''
    Class for the table `provider marketshare`.

    This is where validation happens.

    TODO - Check for SQL injection attacks.
    '''
    def __init__(self,
                 name: str,
                 url: Optional[str],
                 jurisdiction_alpha2: Optional[shared_types.Alpha2],
                 measurement_scope: str,
                 market: str,
                 marketshare: float,
                 time: pd.Timestamp):
        assert(shared_utils.is_nonempty_str(name))
        self.name = name

        if url is None:
            self.url = None
        else:
            assert(shared_utils.is_nonempty_str(url))
            self.url = url

        if jurisdiction_alpha2 is None:
            self.jurisdiction_alpha2 = None
        else:
            assert(type(jurisdiction_alpha2) == shared_types.Alpha2)
            # we'll just store the str version
            self.jurisdiction_alpha2 = str(jurisdiction_alpha2)

        assert(validate_measurement_scope(measurement_scope))
        self.measurement_scope = measurement_scope

        assert(shared_utils.is_nonempty_str(market))
        self.market = market

        assert(is_float_0_1(marketshare))
        self.marketshare = marketshare

        assert(type(time) == pd.Timestamp)
        self.time = time

    def create_table(
            self,
            cur: cursor,
            conn: connection):
        cmd = '''
        CREATE TABLE provider_marketshare (
        primary_id          INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        name                VARCHAR NOT NULL,
        url                 VARCHAR,
        jurisdiction_alpha2 CHAR(2),
        measurement_scope   VARCHAR NOT NULL,
        market              VARCHAR NOT NULL,
        marketshare         NUMERIC NOT NULL,
        time                TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        '''
        cur.execute(cmd)
        conn.commit()

    def write_to_db(
            self,
            cur: cursor,
            conn: connection,
            commit=True,
    ):
        cur.execute(
            """
            INSERT INTO provider_marketshare
            (name, url, jurisdiction_alpha2, measurement_scope, market, marketshare, time)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s)
            """, (self.name,
                  self.url,
                  self.jurisdiction_alpha2,
                  self.measurement_scope,
                  self.market,
                  self.marketshare,
                  self.time))
        if commit:
            return conn.commit()
        return

    def __str__(self):
        return f'{self.name} {self.url} {self.jurisdiction_alpha2} {self.measurement_scope} {self.market} {self.marketshare} {self.time}'

    def __repr__(self):
        return self.__str__()

class CountryMarketshare():
    '''
    Class for the table `country_marketshare`.

    This is where validation happens.

    TODO - Check for SQL injection attacks.
    '''
    def __init__(self,
                 date: pd.Timestamp,
                 jurisdiction_alpha2: Optional[shared_types.Alpha2],
                 measurement_scope: str,
                 market: str,
                 cc_marketshare: float,
                 cc_marketshare_weighted: float,
                 cc_weighted_marketshare: float,
                 total_marketshare: float):
        assert(type(date) == pd.Timestamp)
        self.date = date

        if jurisdiction_alpha2 is None:
            self.jurisdiction_alpha2 = None
        else:
            assert(type(jurisdiction_alpha2) == shared_types.Alpha2)
            # we'll just store the str version
            self.jurisdiction_alpha2 = str(jurisdiction_alpha2)

        assert(validate_measurement_scope(measurement_scope))
        self.measurement_scope = measurement_scope

        assert(shared_utils.is_nonempty_str(market))
        self.market = market

        assert(is_float_0(cc_marketshare))
        self.cc_marketshare = cc_marketshare

        assert(is_float_0(cc_marketshare_weighted))
        self.cc_marketshare_weighted = cc_marketshare_weighted
        
        assert(is_float_0(cc_weighted_marketshare))
        self.cc_weighted_marketshare = cc_weighted_marketshare

        assert(is_float_0_3(total_marketshare))
        self.total_marketshare = total_marketshare

    def create_table(
            self,
            cur: cursor,
            conn: connection):
        cmd = '''
        CREATE TABLE country_marketshare (
        primary_id          INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        date                DATE,
        jurisdiction_alpha2 CHAR(2),
        measurement_scope   VARCHAR NOT NULL,
        market              VARCHAR NOT NULL,
        cc_marketshare         NUMERIC NOT NULL,
        cc_weighted_marketshare    NUMERIC NOT NULL,
        total_marketshare   NUMERIC NOT NULL
        )
        '''
        cur.execute(cmd)
        conn.commit()

    def write_to_db(
            self,
            cur: cursor,
            conn: connection,
            commit=True,
    ):
        cur.execute(
            """
            INSERT INTO country_marketshare
            (date, jurisdiction_alpha2, measurement_scope, market, cc_marketshare, cc_weighted_marketshare, total_marketshare)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s)
            """, (self.date,
                  self.jurisdiction_alpha2,
                  self.measurement_scope,
                  self.market,
                  self.cc_marketshare,
                  self.cc_weighted_marketshare,
                  self.total_marketshare))
        if commit:
            return conn.commit()
        return

    def __str__(self):
        return f'{self.date} {self.jurisdiction_alpha2} {self.measurement_scope} {self.market} {self.cc_marketshare} {self.cc_marketshare_weighted} {self.cc_weighted_marketshare} {self.total_marketshare}'

    def __repr__(self):
        return self.__str__()

class CountryGini ():
    '''
    Class for the table `country_gini`.

    This is where validation happens.

    TODO - Check for SQL injection attacks.
    '''
    def __init__(self,
                 measurement_scope: str,
                 market: str,
                 unweighted_gini: float,
                 gini: float,
                 time: pd.Timestamp):
        assert(shared_utils.is_nonempty_str(market))
        self.market = market

        assert(validate_measurement_scope(measurement_scope))
        self.measurement_scope = measurement_scope

        assert(is_float_0_1(float(unweighted_gini)))
        self.unweighted_gini = unweighted_gini
        
        assert(is_float_0_1(float(gini)))
        self.gini = gini

        assert(type(time) == pd.Timestamp)
        self.time = time

    def create_table(
            self,
            cur: cursor,
            conn: connection):
        cmd = '''
        CREATE TABLE country_gini (
        primary_id          INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        measurement_scope   VARCHAR NOT NULL,
        market              VARCHAR NOT NULL,
        unweighted_gini     NUMERIC NOT NULL,
        gini                NUMERIC NOT NULL,
        time                TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        '''
        cur.execute(cmd)
        conn.commit()

    def write_to_db(
            self,
            cur: cursor,
            conn: connection,
            commit=True,
    ):
        cur.execute(
            """
            INSERT INTO country_gini
            (measurement_scope, market, unweighted_gini, gini, time)
            VALUES
            (%s, %s, %s, %s, %s)
            """, (self.measurement_scope, self.market, self.unweighted_gini, self.gini, self.time))
        if commit:
            return conn.commit()
        return

    def __str__(self):
        return f'{self.measurement_scope} {self.market} {self.unweighted_gini} {self.gini} {self.time}'

    def __repr__(self):
        return self.__str__()


class ProviderGini ():
    '''
    Class for the table `provider_gini`.

    This is where validation happens.

    TODO - Check for SQL injection attacks.
    '''
    def __init__(self,
                 measurement_scope: str,
                 market: str,
                 gini: float,
                 time: pd.Timestamp):
        assert(shared_utils.is_nonempty_str(market))
        self.market = market

        assert(validate_measurement_scope(measurement_scope))
        self.measurement_scope = measurement_scope

        assert(is_float_0_1(float(gini)))
        self.gini = gini

        assert(type(time) == pd.Timestamp)
        self.time = time

    def create_table(
            self,
            cur: cursor,
            conn: connection):
        cmd = '''
        CREATE TABLE provider_gini (
        primary_id          INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        measurement_scope   VARCHAR NOT NULL,
        market              VARCHAR NOT NULL,
        gini                NUMERIC NOT NULL,
        time                TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        '''
        cur.execute(cmd)
        conn.commit()

    def write_to_db(
            self,
            cur: cursor,
            conn: connection,
            commit=True,
    ):
        cur.execute(
            """
            INSERT INTO provider_gini
            (measurement_scope, market, gini, time)
            VALUES
            (%s, %s, %s, %s)
            """, (self.measurement_scope, self.market, self.gini, self.time))
        if commit:
            return conn.commit()
        return

    def __str__(self):
        return f'{self.measurement_scope} {self.market} {self.gini} {self.time}'

    def __repr__(self):
        return self.__str__()


def create_tables(cur: cursor, conn: connection):
    '''
    Create database tables for W3Techs data.
    '''

    # dummy data - just a demo
    ProviderMarketshare(
        'name', None, shared_types.Alpha2('CA'), 'all', 'ssl-certificate', 0.5, pd.Timestamp('2021-04-20')
    ).create_table(cur, conn)
    
    # dummy data - just a demo
    CountryMarketshare(
        pd.Timestamp('2021-04-20'), shared_types.Alpha2('CA'), 'all', 'ssl-certificate', 0.5, 0.6, 1.0
    ).create_table(cur, conn)

    # dummy data - just a demo
    CountryGini(
        'all', 'ssl-certificate', 0.8, 0.9, pd.Timestamp('2021-04-20')
    ).create_table(cur, conn)

    # dummy data - just a demo
    ProviderGini(
        'all', 'ssl-certificate', 0.9, pd.Timestamp('2021-04-20')
    ).create_table(cur, conn)
