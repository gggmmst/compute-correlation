import asyncio as aio
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

from yahoofinance import hist_px

WORKERS = 9


# https://www.pythonsheets.com/notes/python-asyncio.html
# http://cheat.readthedocs.io/en/latest/python/asyncio.html
# https://pymotw.com/3/asyncio/control.html#waiting-for-multiple-coroutines
# https://pymotw.com/3/asyncio/executors.html


@contextmanager
def aio_eventloop():
    loop = aio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


async def async_download_texts(executor, syms, t0, t1):
    func = lambda a: hist_px(*a)
    args = [(t, t0, t1) for t in syms]
    coros = [aio.get_event_loop().run_in_executor(executor, func, arg) for arg in args]
    return await aio.gather(*coros)


def download_texts(syms, t0, t1):

    with aio_eventloop() as loop, ThreadPoolExecutor(max_workers=WORKERS) as executor:
        results = loop.run_until_complete(async_download_texts(executor, syms, t0, t1))

    return results


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
