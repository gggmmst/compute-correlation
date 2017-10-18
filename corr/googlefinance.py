# import requests as rq

import httputils as uhttp
import dateutils as udate

baseurl = 'https://finance.google.com/finance/historical'

def hist_px(ticker, t0, t1):

    ticker = ticker.upper()
    t0 = udate.datestr_to_datetime(t0).strftime('%Y%m%d')
    t1 = udate.datestr_to_datetime(t1).strftime('%Y%m%d')

    payload = {'output'   : 'csv',
               'startdate': t0,
               'enddate'  : t1,
               'q'        : ticker}

    # http GET
    res = uhttp.get_with_retry(baseurl, params=payload)

    if res is None:
        print('Failed to download data (ticker={}, startdate={}, enddate={}) from google finance.'.format(ticker, t0, t1))
        return None

    return res.text


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
