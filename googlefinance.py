import requests as rq

# from http import get_with_retry

baseurl = 'https://finance.google.com/finance/historical'

def hist_px(ticker, t0, t1):

    payload = {'output'   : 'csv',
               'startdate': t0,
               'enddate'  : t1,
               'q'        : ticker}

    # res = get_with_retry(baseurl, params=payload)
    # if res is None:
    #     return None
    # return res.text

    # LOG.info(res.url)

    res = rq.get(baseurl, params=payload)

    if not res.status_code == rq.codes.ok:
        res.raise_for_status()
    return res.text


def get_args():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-s', '--sym', '--symbol', action='store', dest='sym', help='ticker symbol')
    p.add_argument('--t0', '--start', '--startdate', action='store', dest='t0', help='start date')
    p.add_argument('--t1', '--end', '--enddate', action='store', dest='t1', help='end date')
    args = p.parse_args()

    # pre-process
    args.sym = args.sym.upper()         # ticker uppercase

    return args


def main():
    a = get_args()
    px = hist_px(a.sym, a.t0, a.t1)
    print px

if __name__ == '__main__':
    main()

