import pandas as pd

# def get_column(s):
#     colnames = {'*' : '*',
#                 's' : 'sym',
#                 'd' : 'date',
#                 'o' : 'open',
#                 'h' : 'high',
#                 'l' : 'low',
#                 'c' : 'close',
#                 'a' : 'adjclose',
#                 'v' : 'volume'}
#     nicknames = {'sym'     : 's',
#                  'date'    : 'd', 'Date'     : 'd',
#                  'open'    : 'o', 'Open'     : 'o',
#                  'high'    : 'h', 'High'     : 'h',
#                  'low'     : 'l', 'Low'      : 'l',
#                  'close'   : 'c', 'Close'    : 'c',
#                  'adjclose': 'a', 'Adj Close': 'a',
#                  'volume'  : 'v', 'Volume'   : 'v'}
#     if s in colnames:
#         return colnames[s]
#     if s in nicknames:
#         return colnames[nicknames[s]]
#     return None

# db column names
colnames_db = {'*' : '*',
               's' : 'sym',
               'd' : 'date',
               'o' : 'open',
               'h' : 'high',
               'l' : 'low',
               'c' : 'close',
               'a' : 'adjclose',
               'v' : 'volume'}

# yahoo finance column names
colnames_yf = {'o' : 'Open',
               'h' : 'High',
               'l' : 'Low',
               'c' : 'Close',
               'a' : 'Adj Close',
               'v' : 'Volume'}

def _nodb(syms, t0, t1, col='a'):

    try:
        from io import StringIO
    except ImportError:
        from cString import StringIO
    from collections import OrderedDict
    from download import download_texts

    def text_to_ts(text, colname):
        csv = StringIO(text)
        return pd.read_csv(csv, index_col=0, parse_dates=True)[colname]

    texts = download_texts(syms, t0, t1)
    colname = colnames_yf[col]
    # px = dict((sym, text_to_ts(text, colname)) for sym, text in zip(syms, texts))
    px = OrderedDict((sym, text_to_ts(text, colname)) for sym, text in zip(syms, texts))
    df = pd.DataFrame(px)
    return df


def _ondemand(syms, t0, t1, col='a'):
    from cache import get_data
    colname = colnames_db[col]
    data = get_data(syms, t0, t1, colname)
    df = pd.DataFrame(data)
    df = df[list(syms)]      # keep colnames in original order
    return df


def test():
    t0 = '2015-10-10'
    t1 = '2015-11-11'
    syms = ('AAPL', 'MSFT', 'GOOG', 'XLK', 'GS', 'BAC', 'JPM', 'XLF')

    texts = download_texts(syms, t0, t1)
    px = dict((sym, text_to_ts(text, 'Adj Close')) for sym, text in zip(syms, texts))
    df = pd.DataFrame(px)
    print(df.corr())


def test2():
    t0 = '2015-04-22'
    t1 = '2015-06-11'
    syms = ('AAPL', 'MSFT', 'GOOG', 'XLK', 'GS', 'BAC', 'JPM', 'XLF')

    data = get_data(syms, t0, t1)
    df = pd.DataFrame(data)
    df = df[list(syms)]      # keep colnames in original order
    print(df)


def get_args():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-s', '--stocks', '--syms', '--symbols', nargs='+', action='store', required=True, dest='syms', help='list of stock symbols')
    p.add_argument('--start-date', '--t0', '--start', '--startdate', action='store', required=True, dest='t0', help='start date (inclusive)')
    p.add_argument('--last-date', '--t1', '--end', '--enddate', action='store', required=True, dest='t1', help='end date (inclusive)')
    p.add_argument('--nodb', '--no-db', action='store_true', dest='nodb', help='use (download) online data, disable offline cache')
    p.add_argument('-c', '--column', action='store', default='a', dest='col', help='o=open, h=high, l=low, c=close, a=adjclose, v=volume')
    args = p.parse_args()

    # pre-process
    if len(args.syms) == 1:
        args.syms = args.syms[0].split(',')
    args.syms = [s.upper() for s in args.syms]
    # args.t0 = datestr_to_datetime(args.t0).strftime('%Y-%m-%d')
    # args.t1 = datestr_to_datetime(args.t1).strftime('%Y-%m-%d')

    return args


def main():
    args = get_args()
    print(args)
    workhorse = _nodb if args.nodb else _ondemand
    df = workhorse(args.syms, args.t0, args.t1, args.col)
    # print(df)
    print(df.corr())

    # import pdb
    # pdb.set_trace()


if __name__ == '__main__':
    main()
    # test2()

