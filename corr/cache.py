from dateutils import datestr_to_datetime
from download import download_texts
from db import insert_rows, fetch
from holidays import trading_dates
from iterutils import flatten


def text_to_tokens(sym, text):
    lines = text.strip().split('\n')[1:]            # split by newline and drop header
    lines = [sym + ',' + line for line in lines]    # prepend each line with sym
    return [line.split(',') for line in lines]      # finally split each line by comma


def db_has_it(sym, t0, t1):
    """Check if db already has the data we need"""

    # convert datestr to yyyy-mm-dd format
    t0 = datestr_to_datetime(t0).strftime('%Y-%m-%d')
    t1 = datestr_to_datetime(t1).strftime('%Y-%m-%d')

    # dates we need (to download, potentially)
    need = set(trading_dates(t0, t1))
    # dates we have (from db cache)
    have = set(flatten(fetch(sym, t0, t1, cols='date')))

    # compute set diff and determine if download is needed
    return len(need - have) == 0


class CacheException(Exception):
    pass


class Cache(object):

    def __init__(self, syms, t0, t1, cols='*'):
        self.syms = [sym.upper() for sym in syms]
        self.t0 = datestr_to_datetime(t0).strftime('%Y-%m-%d')
        self.t1 = datestr_to_datetime(t1).strftime('%Y-%m-%d')
        self.cols = cols
        # self.column = self.column_name(column)
        # if self.column is None:
        #     raise CacheException('Unknown column: {}'.format(column))

    def get_data(self):
        syms_offline = set(sym for sym in self.syms if db_has_it(sym, self.t0, self.t1))
        syms_online = set(self.syms) - syms_offline
        print('offline:', syms_offline)     # TODO logging.info
        print('online:', syms_online)      # TODO logging.info
        # return {**self.data_online(syms_online), **self.data_offline(syms_offline)}       # py3 only
        data = {}
        if len(syms_online) > 0:
            data.update(self.data_online(syms_online))
        if len(syms_offline) > 0:
            data.update(self.data_offline(syms_offline))
        return data

    def data_offline(self, syms):
        return dict((sym, flatten(fetch(sym, self.t0, self.t1, cols=self.cols))) for sym in syms)

    def data_online(self, syms):
        texts = download_texts(syms, self.t0, self.t1)  # download (text) data
        for sym, text in zip(syms, texts):
            tokens = text_to_tokens(sym, text)          # process text to tokens
            nrows = insert_rows(tokens)                 # insert tokens to db
            print('{} new rows inserted to {}'.format(nrows, sym))      # TODO logging.info
        return self.data_offline(syms)

    # def data_online(self, syms):
    #     texts = download_texts(syms, self.t0, self.t1)  # download (text) data
    #     data = {}
    #     for sym, text in zip(syms, texts):
    #         tokens = text_to_tokens(sym, text)          # process text to tokens
    #         ticker, date, open, high, low, close, adjclose, volume = zip(*tokens)
    #         data[sym] = [float(x) for x in adjclose]    # px data to be returned
    #         nrows = insert_rows(tokens)                 # insert tokens to db
    #         print('{} new rows inserted to {}'.format(nrows, sym))      # TODO logging.info
    #     return data


def get_data(syms, t0, t1, cols):
    c = Cache(syms, t0, t1, cols)
    return c.get_data()
