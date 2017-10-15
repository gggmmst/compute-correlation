import re
# import requests as rq
# from datetime import datetime, timedelta

import utils.http as http
import utils.date as date

fmt_metaurl = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
pat_crumb = r'"CrumbStore":{"crumb":"(.*?)"}'


def crumb_and_cookie(ticker):
    metaurl = fmt_metaurl.format(ticker)
    res = http.get(metaurl)
    cookie = res.headers.get('set-cookie')
    # TODO re.search no match?
    crumb = re.search(pat_crumb, res.text).group(1)
    return crumb, cookie


def hist_px(ticker, t0, t1):

    ticker = ticker.upper()

    crumb, cookie = crumb_and_cookie(ticker)
    baseurl = 'https://query1.finance.yahoo.com/v7/finance/download/{}'.format(ticker)
    payload = {'period1' : date.datestr_to_epoch(t0),
               'period2' : date.datestr_to_epoch(t1),
               'interval': '1d',
               'events'  : 'history',
               'crumb'   : crumb}

    res = http.post_with_retry(baseurl, params=payload, cookies={'Cookie': cookie})

    if res is None:
        print 'Failed to download data from yahoo finance.'
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
    args.t0 = date.datestr_offset(args.t0, 1)
    args.t1 = date.datestr_offset(args.t1, 1)

    return args

# try:
#     from cStringIO import StringIO
# except ImportError:
#     from StringIO import StringIO
# import pandas as pd
# df = pd.read_csv(StringIO(raw.decode('utf-8')))
# print df


def main():
    a = get_args()
    px = hist_px(a.sym, a.t0, a.t1)
    print px

if __name__ == '__main__':
    main()
