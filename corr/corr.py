import logging
import pandas as pd

if __name__ == '__main__':
    from _logging import *
LOG = logging.getLogger(__name__)


############################################################


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


############################################################


def _nodb(syms, t0, t1, col='a'):
    """\
    Get price data online as if db/cache does not exist

    Args:
        syms (list of str) : a list of stock symbols, e.g. ['SPY', 'XLK', 'XLF']
        t0 (str)           : start date datestr, e.g. '2016-01-01'
        t1 (str)           : last date datestr,  e.g. '2016-06-06'
        col (str)          : a character in colnames_yf.keys()

    Returns:
        A dataframe with price data
    """

    try:
        from io import StringIO
    except ImportError:
        from cString import StringIO
    from collections import OrderedDict
    from download import download_texts

    def text_to_ts(text, colname):
        # convert text (csv-string) to DataFrame
        # read_csv accepts stream/buffer, so StringIO is used to convert str->stream
        csv = StringIO(text)
        return pd.read_csv(csv, index_col=0, parse_dates=True)[colname]

    texts = download_texts(syms, t0, t1)
    colname = colnames_yf[col]
    # without ordered dict, the syms order will be shuffled
    # px = dict((sym, text_to_ts(text, colname)) for sym, text in zip(syms, texts))
    px = OrderedDict((sym, text_to_ts(text, colname)) for sym, text in zip(syms, texts))
    df = pd.DataFrame(px)
    return df


def _ondemand(syms, t0, t1, col='a'):
    """\
    Get price data with the following policy:
        - use offline data if db/cache has it
        - on demand download data from online sources if db/cache does not have the data required
        - save downloaded data to db/cache
        - return price data

    Args:
        syms (list of str) : a list of stock symbols, e.g. ['SPY', 'XLK', 'XLF']
        t0 (str)           : start date datestr, e.g. '2016-01-01'
        t1 (str)           : last date datestr,  e.g. '2016-06-06'
        col (str)          : a character in colnames_yf.keys()

    Returns:
        A dataframe with price data
    """

    from cache import get_data
    colname = colnames_db[col]
    data = get_data(syms, t0, t1, colname)
    df = pd.DataFrame(data)
    df = df[list(syms)]         # keep syms in original order
    return df


############################################################


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


# def test():
#     t0 = '2015-10-10'
#     t1 = '2015-11-11'
#     syms = ('AAPL', 'MSFT', 'GOOG', 'XLK', 'GS', 'BAC', 'JPM', 'XLF')

#     texts = download_texts(syms, t0, t1)
#     px = dict((sym, text_to_ts(text, 'Adj Close')) for sym, text in zip(syms, texts))
#     df = pd.DataFrame(px)
#     print(df.corr())


# def test2():
#     t0 = '2015-04-22'
#     t1 = '2015-06-11'
#     syms = ('AAPL', 'MSFT', 'GOOG', 'XLK', 'GS', 'BAC', 'JPM', 'XLF')

#     data = get_data(syms, t0, t1)
#     df = pd.DataFrame(data)
#     df = df[list(syms)]      # keep colnames in original order
#     print(df)


def main():
    args = get_args()
    # print(args)

    workhorse = _nodb if args.nodb else _ondemand   # choose policy
    df = workhorse(args.syms, args.t0, args.t1, args.col)
    # print(df)

    # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.corr.html
    # compute pearson correlation coefficient and print result to stdout
    print(df.corr())

    # import pdb
    # pdb.set_trace()


if __name__ == '__main__':
    main()

