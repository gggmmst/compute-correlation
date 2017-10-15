import re
import requests as rq
from datetime import datetime, timedelta


fmt_metaurl = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
pat_crumb = r'"CrumbStore":{"crumb":"(.*?)"}'


def crumb_and_cookie(ticker):
    metaurl = fmt_metaurl.format(ticker)
    res = rq.get(metaurl)
    cookie = res.headers.get('set-cookie')
    # TODO re.search no match?
    crumb = re.search(pat_crumb, res.text).group(1)
    return crumb, cookie


def datestr_to_epoch(datestr, fmt='%Y-%m-%d'):
    dt = datetime.strptime(datestr, fmt)
    return dt.strftime('%s')


def datestr_offset(datestr, inc=1, fmt='%Y-%m-%d'):
    dt = datetime.strptime(datestr, fmt)
    dt += timedelta(days=inc)
    return dt.strftime(fmt)

from functools import wraps, partial
import time

from requests.exceptions import RequestException

# alternative requests retry
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def request_with_retry(req, attempts=4, delay=1, backoff=1.6):
    # variable scope of nested functions in python2
    # https://eli.thegreenplace.net/2011/05/15/understanding-unboundlocalerror-in-python
    @wraps(req)
    def _retry(attemtps, delay, backoff, *a, **kw):
        for attempt in xrange(attemtps):
            try:
                res = req(*a, **kw)
                if not res.status_code == rq.codes.ok:
                    res.raise_for_status()
                return res
            except RequestException as ex:
                print ex        # TODO make logging
                print 'Request attempt #{} failed, retry in {} seconds ...'.format(attempt+1, delay)   # TODO logging
                time.sleep(delay)
                delay *= backoff
            except Exception as ex:
                print ex    # TODO make logging
        print 'Failed to connect server: maximum request attemtps({}) reached.'.format(attemtps)
        return None

    return partial(_retry, attempts, delay, backoff)



def hist_px(ticker, t0, t1):

    ticker = ticker.upper()

    crumb, cookie = crumb_and_cookie(ticker)
    baseurl = 'https://query1.finance.yahoo.com/v7/finance/download/{}'.format(ticker)
    payload = {'period1' : datestr_to_epoch(t0),
               'period2' : datestr_to_epoch(t1),
               'interval': '1d',
               'events'  : 'history',
               'crumb'   : crumb}

    # LOG.info(res.url)

    res = request_with_retry(rq.post)(baseurl, params=payload, cookies={'Cookie': cookie})
    if res is None:
        print 'Failed to download data from yahoo finance.'
        return None

    # res = retry(rq.post(baseurl, params=payload, cookies={'Cookie': cookie}))
    # if not res.status_code == rq.codes.ok:
    #     res.raise_for_status()

    return res.text


def get_args():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-s', '--sym', '--symbol', action='store', dest='sym', help='ticker symbol')
    p.add_argument('--t0', '--start', '--startdate', action='store', dest='t0', help='start date')
    p.add_argument('--t1', '--end', '--enddate', action='store', dest='t1', help='end date')
    args = p.parse_args()

    # pre-process
    args.sym = args.sym.upper()
    args.t0 = datestr_offset(args.t0, 1)
    args.t1 = datestr_offset(args.t1, 1)

    return args

# try:
#     from cStringIO import StringIO
# except ImportError:
#     from StringIO import StringIO
# import pandas as pd
# df = pd.read_csv(StringIO(raw.decode('utf-8')))
# print df

def test_datestr_offset():
    print datestr_offset('2010-01-01')
    print datestr_offset('2010-01-01', -1)
    print datestr_offset('2010-12-31')
    print datestr_offset('2010-12-31', -1)

def main():
    a = get_args()
    px = hist_px(a.sym, a.t0, a.t1)
    print px

if __name__ == '__main__':
    main()
