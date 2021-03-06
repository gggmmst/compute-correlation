import logging
import re

import httputils as uhttp
import dateutils as udate


if __name__ == '__main__':
    from _logging import *
LOG = logging.getLogger(__name__)


############################################################
## Consts
##

fmt_metaurl = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
fmt_baseurl = 'https://query1.finance.yahoo.com/v7/finance/download/{}'
pat_crumb = r'"CrumbStore":{"crumb":"(.*?)"}'


############################################################
## Helpers
##

class YahooFinanceException(Exception):
    def __init__(self, msg):
        super(YahooFinanceException, self).__init__(msg)
        LOG.error(msg, exc_info=True)


def crumb_and_cookie(sym):

    metaurl = fmt_metaurl.format(sym)
    res = uhttp.get_with_retry(metaurl)     # http GET

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


############################################################
## API
##

def hist_px(sym, t0, t1):

    sym = sym.upper()
    t1 = udate.datestr_offset(t1, 1)    # without this, t1 will not be included
                                        # i.e. yahoofinance excludes enddate by default
                                        # so we need to increment enddate by 1d manually

    baseurl = fmt_baseurl.format(sym)

    crumb, cookie = crumb_and_cookie(sym)

    payload = {'period1' : int(udate.datestr_to_epoch(t0)),
               'period2' : int(udate.datestr_to_epoch(t1)),
               'interval': '1d',
               'events'  : 'history',
               'crumb'   : crumb}

    # http POST
    res = uhttp.post_with_retry(baseurl, params=payload, cookies={'Cookie': cookie})

    if res is None:
        LOG.error('Failed to download data (sym={}, startdate={}, enddate={}) from yahoo finance.'.format(sym, t0, t1))
        return None

    return res.text


############################################################


def get_args():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-s', '--stock', '--sym', '--symbol', action='store', required=True, dest='sym', help='ticker symbol')
    p.add_argument('--start-date', '--t0', '--start', '--startdate', action='store', required=True, dest='t0', help='start date (inclusive)')
    p.add_argument('--last-date', '--t1', '--end', '--enddate', action='store', required=True, dest='t1', help='end date (inclusive)')
    return p.parse_args()


def main():
    a = get_args()
    px = hist_px(a.sym, a.t0, a.t1)
    print(px)

if __name__ == '__main__':
    main()
