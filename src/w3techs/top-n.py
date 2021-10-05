# taaraxtak
# nick merrill
# 2021
#
# w3techs
# top-n.py - collects data and saves it in the db.

import psycopg2
import logging
import pandas as pd
import sys
sys.path.append("/home/pulse/taaraxtak/")

from os.path import join
from os import listdir
from src.shared.utils import get_country
from datetime import datetime
from config import config
# from imp import reload

postgres_config = config['postgres']
conn = psycopg2.connect(**postgres_config)
cur = conn.cursor()

def parse_df (df: pd.DataFrame) -> pd.DataFrame:
    '''
    Returns a df with columns
    name, marketshare
    '''
    def percentify (x):
        try:
            n = x.split('%')[0]
            return float(n)/100
        except:
            return 0
    # percentages are in second column
    df['marketshare'] = df[df.columns[1]].apply(percentify)
    # we're ignoring heirarchical csv files,
    # get names from 0th column
    df['name'] = df[df.columns[0]]
    # get jurisdictions
    # remove 'and territories' for server locations
    df['name'] = df['name'].apply(lambda x: x.split(' and territories')[0])
    df['jurisdiction_alpha2'] = df['name'].apply(get_country)
    return df[['name', 'marketshare', 'jurisdiction_alpha2']]

included_fn_markets = [
    'web_hosting',
    'ssl_certificate',
    'proxy',
    'data_center',
    'dns_server',
    'server_location',
    'top_level_domain',
]

included_db_markets = [
    'web-hosting',
    'ssl-certificate',
    'proxy',
    'data-centers',
    'dns-server',
    'server-location',
    'top-level-domain',
]

included_scopes = [
    'top_1k',
    'top_10k'
]

included_times = [
    pd.Timestamp('2021-06-02'),
    pd.Timestamp('2021-07-02'),
    pd.Timestamp('2021-08-02'),
    pd.Timestamp('2021-09-02'),
    pd.Timestamp('2021-10-02')
]

dfs = []
for my_dir in listdir('top-sites'):
    fn = my_dir.split('.csv')[0]
    if fn.split('-')[1]!='hierarchy':
        if fn.split('-')[0] in included_fn_markets:
            if fn.split('-')[1] in included_scopes:
                market, top_n, date_str  = fn.split('-')
                date = datetime.strptime(date_str, '%Y%m')
                print(market, top_n, date)
                df = pd.read_csv(join('top-sites', my_dir))
                df = parse_df(df)
                df['measurement_scope'] = top_n
                df['market'] = market
                df['date'] = date
                dfs.append(df)
df = pd.concat(dfs)

df.market = df.market.replace({
    'dns_server': 'dns-server',
    'server_location': 'server-location',
    'data_center': 'data-centers',
    'ssl_certificate': 'ssl-certificate',
    'web_hosting': 'web-hosting',
    'reverse_proxy': 'proxy',
    'top_level_domain': 'top-level-domain',
})

df.to_csv('out/top-sites-combined.csv')

import src.w3techs.types
# reload(src.w3techs.types)
from src.w3techs.types import ProviderMarketshare
from src.shared.types import Alpha2

for i, row in df.iterrows():
    try:
        alpha2 = Alpha2(row.jurisdiction_alpha2)
    except:
        alpha2 = None
    marketshare = ProviderMarketshare(
        row['name'],
        None,
        alpha2,
        row.measurement_scope,
        row.market, 
        float(row['marketshare']),
        pd.Timestamp(row.date))

    marketshare.write_to_db(cur, conn, commit=False)

conn.commit()

import src.w3techs.utils as utils

for time in included_times:
    print(time)
    for measurement_scope in included_scopes:
        print(measurement_scope)
        for market in included_db_markets:
            pop_weighted_gini = utils.population_weighted_gini(cur, measurement_scope, market, time)
            if pop_weighted_gini:
                print(f'[X] pop_weighted {market}')
                pop_weighted_gini.write_to_db(cur, conn)
            else:
                print(f'[ ] pop_weighted {market}')
            unweighted_gini = utils.unweighted_gini(cur, measurement_scope, market, time)
            if unweighted_gini:
                print(f'[X] unweighted {market}')
                unweighted_gini.write_to_db(cur, conn)
            else:
                print(f'[ ] unweighted {market}')
