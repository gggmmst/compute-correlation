import logging
import time
from functools import wraps, partial

import requests as rq
from requests.exceptions import RequestException


if __name__ == '__main__':
    from _logging import *
LOG = logging.getLogger(__name__)


############################################################
## Workhorse
##

# alternative way to call requests with retry
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
# however it looks a lot more dependent and complicated

def request_with_retry(req, attempts=4, delay=1, backoff=1.6):
    # variable scope of nested functions in python2
    # https://eli.thegreenplace.net/2011/05/15/understanding-unboundlocalerror-in-python
    @wraps(req)
    def _retry(attemtps, delay, backoff, *a, **kw):
        for attempt in range(attemtps):
            try:
                res = req(*a, **kw)
                LOG.info('Request with url [{}]'.format(res.url))
                if not res.status_code == rq.codes.ok:
                    res.raise_for_status()
            except RequestException as ex:
                LOG.info('Request attempt #{} failed (reason: {}), retry in {} seconds ...'.format(attempt+1, ex, delay))
                time.sleep(delay)
                delay *= backoff
            except Exception as ex:
                LOG.error(ex, exc_info=True)
            else:
                return res
        LOG.error('Request failed: maximum request attemtps({}) reached.'.format(attemtps))
        return None

    return partial(_retry, attempts, delay, backoff)


############################################################
## API
##

def get(*a, **kw):
    """Normal requests.get"""
    return rq.get(*a, **kw)

def get_with_retry(*a, **kw):
    """requests.get wrapped with retry functionality"""
    f = request_with_retry(rq.get)      # currying
    return f(*a, **kw)

def post(*a, **kw):
    """Normal requests.post"""
    return rq.post(*a, **kw)

def post_with_retry(*a, **kw):
    """requests.post wrapped with retry functionality"""
    f = request_with_retry(rq.post)     # currying
    return f(*a, **kw)

