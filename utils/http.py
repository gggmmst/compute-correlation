
#import logging

import time
from functools import wraps, partial

import requests as rq
from requests.exceptions import RequestException


# alternative way to call requests with retry
# however it looks a lot more complicated/dependent
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests

def request_with_retry(req, attempts=4, delay=1, backoff=1.6):
    # variable scope of nested functions in python2
    # https://eli.thegreenplace.net/2011/05/15/understanding-unboundlocalerror-in-python
    @wraps(req)
    def _retry(attemtps, delay, backoff, *a, **kw):
        for attempt in range(attemtps):
            try:
                res = req(*a, **kw)
                print(res.url)   # TODO logging
                if not res.status_code == rq.codes.ok:
                    res.raise_for_status()
                return res
            except RequestException as ex:
                print(ex)        # TODO make logging
                print('Request attempt #{} failed, retry in {} seconds ...'.format(attempt+1, delay))   # TODO logging
                time.sleep(delay)
                delay *= backoff
            except Exception as ex:
                print(ex)    # TODO make logging
        print('Request failed: maximum request attemtps({}) reached.'.format(attemtps))
        return None

    return partial(_retry, attempts, delay, backoff)


##
## API
##
def get(*a, **kw):
    return rq.get(*a, **kw)

def get_with_retry(*a, **kw):
    f = request_with_retry(rq.get)
    return f(*a, **kw)

def post(*a, **kw):
    return rq.post(*a, **kw)

def post_with_retry(*a, **kw):
    f = request_with_retry(rq.post)
    return f(*a, **kw)
