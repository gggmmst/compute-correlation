import logging
from itertools import product
from datetime import datetime, timedelta


if __name__ == '__main__':
    from _logging import *
LOG = logging.getLogger(__name__)


############################################################
## Consts
##

# date separators/specifiers/formats
date_seps = ['-', '', '.']
date_spec = [('%Y', '%m', '%d')]
date_fmts = [sep.join(t) for sep, t in product(date_seps, date_spec)]

# >>> print(date_fmts)
# ['%Y-%m-%d', '%Y%m%d', '%Y.%m.%d']


############################################################
## API
##

def datestr_to_datetime(datestr, return_fmt=False):
    """\
    Convert date string into datetime object
    Attempt to "guess" datestr format by iterate all the predefined formats (date_fmt)

    # Convert datestr to <datetime obj>
    >>> datestr_to_datetime('20151213')
    datetime.datetime(2015, 12, 13, 0, 0)
    >>> datestr_to_datetime('2015-12-13')
    datetime.datetime(2015, 12, 13, 0, 0)

    # With return_fmt=True, returns a tuple of (<datestr format>, <datetime obj>)
    >>> datestr_to_datetime('2015-12-13', True)
    ('%Y-%m-%d', datetime.datetime(2015, 12, 13, 0, 0))
    >>> datestr_to_datetime('20151213', True)
    ('%Y%m%d', datetime.datetime(2015, 12, 13, 0, 0))
    >>> datestr_to_datetime('2015.12.13', True)
    ('%Y.%m.%d', datetime.datetime(2015, 12, 13, 0, 0))

    Args:
        datestr (str)     : e.g. '20001234', '2000.12.34', '2000-12-34'
        return_fmt (bool) : if True, also return datestr's format

    Returns:
        a datetime object
    """

    for fmt in date_fmts:
        try:
            dt = datetime.strptime(datestr, fmt)
        except ValueError as ex:
            # cannot interpret datestr with assumed format
            # swallow exception and try another format
            LOG.debug(ex)
        else:
            # succeed
            return (fmt, dt) if return_fmt else dt

    # failed
    LOG.error('Failed to parse date string ({}): Invalid date or fail to match these formats {}.'.format(datestr, repr(date_fmts)))
    return None


def datestr_to_epoch(datestr):
    """Convert datestr to Unix epoch"""
    dt = datestr_to_datetime(datestr)
    return dt.strftime('%s')


def datestr_offset(datestr, inc=1, fmt=None):
    """\
    Increment or decrement date string

    >>> datestr_offset('20010101', 1)
    '20010102'
    >>> datestr_offset('20010101', 1, fmt='%Y-%m-%d')
    '2001-01-02'
    >>> datestr_offset('2001-01-01', 1, fmt='%Y.%m.%d')
    '2001.01.02'
    """

    _fmt, dt = datestr_to_datetime(datestr, True)
    if fmt is None:     # assume same as input format if output format is not specified
        fmt = _fmt
    dt += timedelta(days=inc)
    return dt.strftime(fmt)


def idates(start, end, predicate=lambda x:True):
    fmt, d0 = datestr_to_datetime(start, True)
    d1      = datestr_to_datetime(end)
    inc = timedelta(days=1)
    while d0 <= d1:
        if predicate(d0):
            yield d0.strftime(fmt)
        d0 += inc
    raise StopIteration()


def is_weekend(dt):
    """Returns True if given datetime is a weekend"""
    e = dt.weekday()
    return e >= 5               # same as below, but only check 1 cond (as opposed to 2)
    # return e == 5 or e == 6     # saturday OR sunday


def is_weekday(dt):
    """Returns True if given datetime is a weekday"""
    e = dt.weekday()
    return e < 5
    # return e != 5 and e != 6    # not saturday AND not sunday


############################################################


def test_datestr_to_datetime():
    print(datestr_to_datetime('20120101'))
    print(datestr_to_datetime('2017-12-31'))
    print(datestr_to_datetime('2008.09.30'))
    print(datestr_to_datetime('2008.09.31'))    # non-existent date
    print(datestr_to_datetime('2017-12-34'))    # non-existent date

def test_datestr_to_epoch():
    print(datestr_to_epoch('20101111'))
    print(datestr_to_epoch('1970-01-01'))

def test_datestr_offset():
    print(datestr_offset('2010-01-01'))
    print(datestr_offset('20120304', -1))
    print(datestr_offset('20120304', -1, '%Y-%m-%d'))
    print(datestr_offset('2010-12-31'))
    print(datestr_offset('2010-12-31', -1))

def test_idates():
    print(list(idates('20110101', '20110202')))
    print(list(idates('20110101', '20110202', predicate=is_weekday)))
    print(list(idates('20110101', '20110101')))

def test():
    test_datestr_to_datetime()
    test_datestr_to_epoch()
    test_datestr_offset()
    test_idates()

if __name__ == '__main__':
    test()

