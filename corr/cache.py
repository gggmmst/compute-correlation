import logging
from dateutils import datestr_to_datetime
from download import download_texts
from db import insert_rows, fetch
from holidays import trading_dates
from iterutils import flatten


if __name__ == '__main__':
    from _logging import *
LOG = logging.getLogger(__name__)


############################################################
## Workhorse
##

def text_to_tokens(sym, text):
    lines = text.strip().split('\n')[1:]            # split by newline and drop header
    lines = [sym + ',' + line for line in lines]    # prepend each line with sym
    return [line.split(',') for line in lines]      # finally split each line by comma


class CacheException(Exception):
    pass


class Cache(object):
    """\
    Provide data with the following policy:
        - if db has required data (by checking sym and dates),
            then (stay offline) return data
        - otherwise download data online from sources (e.g. yahoofinance/googlefinance),
            then save freshly downloaded data to db,
            and then return data
    """

    @classmethod
    def is_cached(cls, sym, t0, t1):
        """\
        Check if db already has the data we need

        Args:
            sym (str) : ticker symbol
            t0  (str) : start date
            t1  (str) : end date
        Returns:
            True if data required is cached in db; False otherwise
        """
        # convert datestr to yyyy-mm-dd format
        t0 = datestr_to_datetime(t0).strftime('%Y-%m-%d')
        t1 = datestr_to_datetime(t1).strftime('%Y-%m-%d')

        # dates we need (to download, potentially)
        need = set(trading_dates(t0, t1))
        # dates we have (from db cache)
        have = set(flatten(fetch(sym, t0, t1, cols='date')))

        # compute set diff and determine if download is needed
        return len(need - have) == 0


    def __init__(self, syms, t0, t1, cols='*'):
        self.syms = [sym.upper() for sym in syms]
        self.t0 = datestr_to_datetime(t0).strftime('%Y-%m-%d')
        self.t1 = datestr_to_datetime(t1).strftime('%Y-%m-%d')
        self.cols = cols


    def get_data(self):
        # set of syms in which data has (offline) cached
        syms_offline = set(sym for sym in self.syms if self.is_cached(sym, self.t0, self.t1))
        LOG.info('Symbols have (offline) data in db: {}'.format(syms_offline))

        # set of syms in which (online) download is needed
        syms_online = set(self.syms) - syms_offline
        LOG.info('Symbols need (online) data download: {}'.format(syms_online))

        # return {**self.data_online(syms_online), **self.data_offline(syms_offline)}       # oneliner; py3 only
        data = {}                                           # result placeholder
        if len(syms_online) > 0:
            data.update(self.data_online(syms_online))      # download data and update placeholder
        if len(syms_offline) > 0:
            data.update(self.data_offline(syms_offline))    # load data from db and update placeholder

        return data


    def data_offline(self, syms):
        return dict((sym, flatten(fetch(sym, self.t0, self.t1, cols=self.cols))) for sym in syms)


    def data_online(self, syms):
        texts = download_texts(syms, self.t0, self.t1)      # download (text) data
        for sym, text in zip(syms, texts):
            tokens = text_to_tokens(sym, text)              # process text to tokens
            nrows = insert_rows(tokens)                     # insert tokens to db
            LOG.info('{} new rows inserted to {}'.format(nrows, sym))
        return self.data_offline(syms)

    # def data_online(self, syms):
    #     texts = download_texts(syms, self.t0, self.t1)      # download (text) data
    #     data = {}
    #     for sym, text in zip(syms, texts):
    #         tokens = text_to_tokens(sym, text)              # process text to tokens
    #         ticker, date, open, high, low, close, adjclose, volume = zip(*tokens)
    #         data[sym] = [float(x) for x in adjclose]        # px data to be returned
    #         nrows = insert_rows(tokens)                     # insert tokens to db
    #         LOG.info('{} new rows inserted to {}'.format(nrows, sym))
    #     return data


############################################################
## API
##

def get_data(syms, t0, t1, cols='*'):
    c = Cache(syms, t0, t1, cols)
    return c.get_data()

