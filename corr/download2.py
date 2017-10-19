import logging

# https://docs.python.org/2/library/multiprocessing.html#module-multiprocessing.dummy
# multiprocessing.dummy replicates the API of multiprocessing but is no more than a wrapper around the threading module.
from multiprocessing.dummy import Pool

from yahoofinance import hist_px


if __name__ == '__main__':
    from _logging import *
LOG = logging.getLogger(__name__)


############################################################

WORKERS = 9


def process_args(args):
    """\
    A helper function to pre-process args for download_texts

    args is assumed to be of the following either forms:
        1. (sym_1, startdate_1, lastdate_1), ..., (sym_n, startdate_n, lastdate_n)
        2. (sym_1, sym_2, ..., sym_n), startdate, lastdate

    In case 2, this helper function will expand/transform args to the format of case 1.
    """

    if isinstance(args[1], str):                # if second arg is a string, then case 2
        return [(t, args[1], args[2]) for t in args[0]]     # convert format to case 1
    return args


############################################################
## API
##

def download_texts(*args):
    """\
    Spawn a pool of workers to download text asynchronously

    Args:
        Iterable of either these 2 format:
        1. (sym_1, startdate_1, lastdate_1), ..., (sym_n, startdate_n, lastdate_n)
        2. (sym_1, sym_2, ..., sym_n), startdate, lastdate

        In the second case, the same startdate and lastdate will be assumed across all sym's

    Returns:
        A list of downloaded text
    """

    args = process_args(args)
    LOG.info('Spawning {} workers to download data'.format(WORKERS))
    resp = Pool(WORKERS).map(lambda a:hist_px(*a), args)
    return resp


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
    print(download_texts(a.syms, a.t0, a.t1))


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
