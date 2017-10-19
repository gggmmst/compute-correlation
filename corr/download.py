import sys

if sys.version_info >= (3, 5):
    from download3 import download_texts
else:
    from download2 import download_texts


############################################################


def get_args():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-s', '--stocks', '--syms', '--symbols', nargs='+', action='store', required=True, dest='syms', help='list of stock symbols')
    p.add_argument('--start-date', '--t0', '--start', '--startdate', action='store', required=True, dest='t0', help='start date (inclusive)')
    p.add_argument('--last-date', '--t1', '--end', '--enddate', action='store', required=True, dest='t1', help='end date (inclusive)')
    args = p.parse_args()

    # pre-process
    if len(args.syms) == 1:
        args.syms = args.syms[0].split(',')

    return args


def main():
    a = get_args()
    res = download_texts(a.syms, a.t0, a.t1)
    for sym, raw in zip(a.syms, res):
        print(sym)
        print(raw)


def test():
    t0 = '2015-10-10'
    t1 = '2015-11-11'
    syms = ('AAPL', 'MSFT', 'GOOG', 'XLK', 'GS', 'BAC', 'JPM', 'XLF')
    res = download_texts(syms, t0, t1)
    import pdb
    pdb.set_trace()
    return res


if __name__ == '__main__':
    main()
    # test()
