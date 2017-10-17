# import logging

import re
# import requests as rq
# from datetime import datetime, timedelta

import utils.http as http
import utils.dateutils as dateutils


# LOG = logging.getLogger(__name__)


fmt_metaurl = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
fmt_baseurl = 'https://query1.finance.yahoo.com/v7/finance/download/{}'
pat_crumb = r'"CrumbStore":{"crumb":"(.*?)"}'


class YahooFinanceException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        print(msg)
        # LOG.error(msg)
        # LOG.error(msg, exc_info=True)


def crumb_and_cookie(ticker):
    metaurl = fmt_metaurl.format(ticker)
    res = http.get_with_retry(metaurl)     # http GET
    # extract cookie
    cookie = res.headers.get('set-cookie')
    if cookie is None:
        msg = 'Failed to extract cookie from url [{}]'.format(metaurl)
        raise YahooFinanceException(msg)
    # extract crumb
    match = re.search(pat_crumb, res.text)
    if match is None:
        msg = 'Failed to extract crumb from url [{}]'.format(metaurl)
        raise YahooFinanceException(msg)
    crumb = match.group(1)
    return crumb, cookie


def hist_px(ticker, t0, t1):

    t0 = dateutils.datestr_offset(t0, 1)    # yahoo simply wants to make it hard for non-programmers
    t1 = dateutils.datestr_offset(t1, 1)

    baseurl = fmt_baseurl.format(ticker)

    crumb, cookie = crumb_and_cookie(ticker)
    payload = {'period1' : dateutils.datestr_to_epoch(t0),
               'period2' : dateutils.datestr_to_epoch(t1),
               'interval': '1d',
               'events'  : 'history',
               'crumb'   : crumb}

    # http POST
    res = http.post_with_retry(baseurl, params=payload, cookies={'Cookie': cookie})

    if res is None:
        print('Failed to download data (ticker={}, startdate={}, enddate={}) from yahoo finance.'.format(ticker, t0, t1))
        return None

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
    # args.t0 = dateutils.datestr_offset(args.t0, 1)
    # args.t1 = dateutils.datestr_offset(args.t1, 1)

    return args


def main():
    a = get_args()
    px = hist_px(a.sym, a.t0, a.t1)
    print(px)

if __name__ == '__main__':
    main()
