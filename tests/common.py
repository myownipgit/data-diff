import hashlib
import preql

from data_diff import database as db
import logging
import sys
from itertools import product

logging.getLogger("diff_tables").setLevel(logging.WARN)
logging.getLogger("database").setLevel(logging.DEBUG)

TEST_MYSQL_CONN_STRING: str = "mysql://mysql:Password1@localhost/mysql"
TEST_POSTGRES_CONN_STRING: str = "postgres://postgres:Password1@localhost/postgres"
TEST_SNOWFLAKE_CONN_STRING: str = None
TEST_BIGQUERY_CONN_STRING: str = None

try:
    from .local_settings import *
except ImportError:
    pass  # No local settings

CONN_STRINGS = {
    db.MySQL: TEST_MYSQL_CONN_STRING,
    db.Postgres: TEST_POSTGRES_CONN_STRING,
    db.BigQuery: TEST_BIGQUERY_CONN_STRING,     # TODO BigQuery after Snowflake causes an error!
    db.Snowflake: TEST_SNOWFLAKE_CONN_STRING,
}

for k, v in CONN_STRINGS.items():
    if v is None:
        print(f"Warning: Connection to {k} not configured")

CONN_STRINGS = {k: v for k, v in CONN_STRINGS.items() if v is not None}
CONNS = {k: (preql.Preql(v), db.connect_to_uri(v)) for k, v in CONN_STRINGS.items()}

def str_to_checksum(str: str):
    # hello world
    #   => 5eb63bbbe01eeed093cb22bb8f5acdc3
    #   =>                   cb22bb8f5acdc3
    #   => 273350391345368515
    m = hashlib.md5()
    m.update(str.encode("utf-8"))  # encode to binary
    md5 = m.hexdigest()
    # 0-indexed, unlike DBs which are 1-indexed here, so +1 in dbs
    half_pos = db.MD5_HEXDIGITS - db.CHECKSUM_HEXDIGITS
    return int(md5[half_pos:], 16)
