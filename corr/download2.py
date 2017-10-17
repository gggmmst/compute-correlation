from multiprocessing.dummy import Pool

from yahoofinance import hist_px

WORKERS = 9


def download_texts(syms, t0, t1):
    args = [(t, t0, t1) for t in syms]
    resp = Pool(WORKERS).map(lambda a:hist_px(*a), args)
    return resp


def get_args():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-s', '--stocks', '--syms', '--symbols', nargs='+', action='store', dest='syms', help='list of stock symbols')
    p.add_argument('--start-date', '--t0', '--start', '--startdate', action='store', dest='t0', help='start date (inclusive)')
    p.add_argument('--last-date', '--t1', '--end', '--enddate', action='store', dest='t1', help='end date (inclusive)')
    args = p.parse_args()

    # pre-process
    if len(args.syms) == 1:
        args.syms = args.syms[0].split(',')

    return args


def main():
    a = get_args()
    print(download_texts(a.syms, a.t0, a.t1))


def test():
    t0 = '2015-10-10'
    t1 = '2015-11-11'
    tickers = ('AAPL', 'MSFT', 'GOOG', 'XLK', 'GS', 'BAC', 'JPM', 'XLF')
    res = download_texts(tickers, t0, t1)
    import pdb
    pdb.set_trace()
    return res


if __name__ == '__main__':
    main()
    # test()
