# taaraxtak
# nick merrill
# 2021
#
# create-tables.py - sets up database tables
# run this once.

from funcy import partial
import logging
import psycopg2

from src.w3techs.types import create_tables as w3techs_create
from src.ooni.types import create_tables as ooni_create

from config import config
from src.shared.utils import configure_logging
#
# setup
#
logger = configure_logging()

# connect to the db
connection = psycopg2.connect(**config['postgres'])
cursor = connection.cursor()

# configure create methods for the db
w3techs = partial(w3techs_create, cursor, connection)
ooni = partial(ooni_create, cursor, connection)

#
# run
#
w3techs()
ooni()
