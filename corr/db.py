import sqlite3

from contextlib import contextmanager


DBPATH = 'yahoofinance.db'
CONN = sqlite3.connect(DBPATH)


sql_create = '''\
CREATE TABLE IF NOT EXISTS stocks (
  sym      TEXT,
  date     TEXT,
  open     REAL,
  high     REAL,
  low      REAL,
  close    REAL,
  adjclose REAL,
  volume   INTEGER,
  PRIMARY KEY (sym, date)
)'''


sql_insert = '''\
INSERT INTO stocks
  (sym, date, open, high, low, close, adjclose, volume)
VALUES
  (?,?,?,?,?,?,?,?)'''


sql_select = '''\
SELECT {}
FROM stocks
WHERE (sym = ?) AND (date BETWEEN ? AND ?)
ORDER BY date'''


@contextmanager
def cursor(conn):
    try:
        yield conn.cursor()
    except sqlite3.OperationalError as ex:
        if ex.message.startswith('no such table'):
            # create table if not exists
            with conn:
                conn.execute(sql_create)
    else:
        conn.commit()


def insert_rows(rows, conn=CONN):
    count = 0
    for row in rows:
        try:
            with cursor(conn) as c:
                c.execute(sql_insert, row)
        except sqlite3.IntegrityError as ex:
            print('Failed to insert {}: {}'.format(row, ex))    # logging.info
        except Exception as ex:
            print(ex)           # TODO logging.err
        else:
            count += 1
    return count


def fetch(sym, t0='1900-01-01', t1='2200-12-31', cols='*', conn=CONN):
    try:
        with cursor(conn) as c:
            c.execute(sql_select.format(cols), (sym, t0, t1))
    except Exception as ex:
        print(ex)   # TODO logging.error
    else:
        return c.fetchall()

