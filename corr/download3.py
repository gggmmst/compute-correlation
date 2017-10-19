############################################################
## Notes
##

# https://www.pythonsheets.com/notes/python-asyncio.html
# http://cheat.readthedocs.io/en/latest/python/asyncio.html
# https://pymotw.com/3/asyncio/control.html#waiting-for-multiple-coroutines
# https://pymotw.com/3/asyncio/executors.html


############################################################


import logging
import asyncio as aio
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

from yahoofinance import hist_px

if __name__ == '__main__':
    from _logging import *
LOG = logging.getLogger(__name__)


WORKERS = 9


############################################################
## Helpers
##

@contextmanager
def aio_eventloop():
    loop = aio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


async def async_download_texts(executor, args):
    """A coroutine that put tasks to run in an executor and collection (gather) task results"""
    func = lambda a: hist_px(*a)
    coros = [aio.get_event_loop().run_in_executor(executor, func, arg) for arg in args]
    return await aio.gather(*coros)


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
    with aio_eventloop() as loop, ThreadPoolExecutor(max_workers=WORKERS) as executor:
        # fire coroutines to download texts asynchronously
        # blocks until tasks finish and return a list of results
        results = loop.run_until_complete(async_download_texts(executor, args))

    return results


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
