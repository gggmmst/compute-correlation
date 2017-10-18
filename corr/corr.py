import pandas as pd


def _nodb(syms, t0, t1):

    try:
        from io import StringIO
    except ImportError:
        from cString import StringIO
    from download import download_texts

    def text_to_ts(text, colname='Close'):
        csv = StringIO(text.decode('utf-8'))
        return pd.read_csv(csv, index_col=0, parse_dates=True)[colname]

    texts = download_texts(syms, t0, t1)
    # px = dict((ticker, text_to_ts(text, 'Adj Close')) for ticker, text in zip(syms, texts))
    px = dict((ticker, text_to_ts(text)) for ticker, text in zip(syms, texts))
    df = pd.DataFrame(px)
    return df


def _ondemand(syms, t0, t1):
    from cache import get_data
    data = get_data(syms, t0, t1)
    df = pd.DataFrame(data)
    df = df[list(syms)]      # keep colnames in original order
    return df


def test():
    t0 = '2015-10-10'
    t1 = '2015-11-11'
    syms = ('AAPL', 'MSFT', 'GOOG', 'XLK', 'GS', 'BAC', 'JPM', 'XLF')

    texts = download_texts(syms, t0, t1)
    px = dict((ticker, text_to_ts(text, 'Adj Close')) for ticker, text in zip(syms, texts))
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
    p.add_argument('--no-db', action='store_true', dest='nodb', help='use (download) online data, disable offline cache')
    args = p.parse_args()

    # pre-process
    if len(args.syms) == 1:
        args.syms = args.syms[0].split(',')

    return args


def main():
    args = get_args()
    print(args)
    workhorse = _nodb if args.nodb else _ondemand
    df = workhorse(args.syms, args.t0, args.t1)
    # print(df)
    print(df.corr())

    # import pdb
    # pdb.set_trace()


if __name__ == '__main__':
    main()
    # test2()

