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
    ## XXX
    # t0 = datestr_to_datetime(t0).strftime('%Y-%m-%d')
    # t1 = datestr_to_datetime(t1).strftime('%Y-%m-%d')
    # print(t0, t1)
    ## FIXME
    # dates we need (to download, potentially)
    need = set(trading_dates(t0, t1))
    # dates we have (from db cache)
    have = set(s.encode('utf-8') for s in flatten(fetch(sym, t0, t1, cols='date')))
    return len(need - have) == 0


class Cache(object):

    def __init__(self, syms, t0, t1):
        self.syms = syms
        self.t0 = t0
        self.t1 = t1

    def get_data(self):
        syms_offline = set(sym for sym in self.syms if db_has_it(sym, self.t0, self.t1))
        syms_online = set(self.syms) - syms_offline
        print('offline:', syms_offline)     # TODO logging.info
        print('online:', syms_online)      # TODO logging.info
        data = {}
        data.update(self.data_online(syms_online))
        data.update(self.data_offline(syms_offline))
        return data

    def data_offline(self, syms):
        return dict((sym, flatten(fetch(sym, self.t0, self.t1, cols='adjclose'))) for sym in syms)
        # return dict((sym, flatten(fetch(sym, self.t0, self.t1, cols='close'))) for sym in syms)

    def data_online(self, syms):
        texts = download_texts(syms, self.t0, self.t1)  # download (text) data
        data = {}
        inserted = {}
        for sym, text in zip(syms, texts):
            tokens = text_to_tokens(sym, text)          # process text to tokens
            ticker, date, open, high, low, close, adjclose, volume = zip(*tokens)
            data[sym] = map(float, adjclose)            # px data to be returned
            # data[sym] = map(float, close)            # px data to be returned
            inserted[sym] = insert_rows(tokens)         # insert tokens to db
        print(inserted)         # TODO logging.info
        return data


def get_data(syms, t0, t1):
    c = Cache(syms, t0, t1)
    return c.get_data()


# def db_has_it(sym, t0, t1):
#     """Check if db already has the data we need"""
#     # dates we need (to download, potentially)
#     need = set(trading_dates(t0, t1))
#     # dates we have (from db cache)
#     have = set(s.encode('utf-8') for s in flatten(fetch(sym, t0, t1, cols='date')))
#     return len(need - have) == 0


# # insert_rows(text_to_tokens(sym, download_texts(sym, t0, t1)[0]))

# def data_offline(syms, t0, t1):
#     return dict((sym, flatten(fetch(sym, t0, t1, cols='adjclose'))) for sym in syms)


# # def data_online(syms, t0, t1):
# #     texts = download_texts(syms, t0, t1)
# #     inserted = dict((sym, insert_rows(text_to_tokens(sym, text))) for sym, text in zip(syms, texts))
# #     print(inserted)         # TODO logging.info
# #     return data_offline(syms, t0, t1)


# def data_online(syms, t0, t1):
#     texts = download_texts(syms, t0, t1)
#     data = {}
#     inserted = {}
#     for sym, text in zip(syms, texts):
#         tokens = text_to_tokens(sym, text)
#         ticker, date, open, high, low, close, adjclose, volume = zip(*tokens)
#         data[sym] = map(float, adjclose)
#         inserted[sym] = insert_rows(tokens)
#     print(inserted)         # TODO logging.info
#     return data




# uu = fetch('GOOG', '2015-02-02', '2015-04-04', cols='date,adjclose')
# pd.DataFrame(dict(zip(('date', 'GOOG'), zip(*uu)))).set_index('date')
