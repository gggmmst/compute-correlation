# import logging
from itertools import product
from datetime import datetime, timedelta

# LOG = logging.getLogger(__name__)

# date separators/specifiers/formats
date_seps = ['-', '', '.']
date_spec = [('%Y', '%m', '%d')]
date_fmts = [sep.join(t) for sep, t in product(date_seps, date_spec)]

# >>> print(date_fmts)
# ['%Y-%m-%d', '%Y%m%d', '%Y.%m.%d']


##################################################
## API
##

def datestr_to_datetime(datestr, keep_fmt=False):
    """\
    Convert date string into datetime object.
    """
    for fmt in date_fmts:
        try:
            dt = datetime.strptime(datestr, fmt)
        except ValueError as ex:
            print(ex)   # TODO logging debug
        else:
            return (fmt, dt) if keep_fmt else dt
    m = 'Failed to parse date string ({}): Invalid date or fail to match these formats {}.'.format(datestr, repr(date_fmts))
    print(m)        # TODO logging error
    return None


def datestr_to_epoch(datestr):
    dt = datestr_to_datetime(datestr)
    return dt.strftime('%s')


def datestr_offset(datestr, inc=1, fmt=None):
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
    e = dt.weekday()
    return e == 5 or e == 6     # saturday or sunday


def is_weekday(dt):
    e = dt.weekday()
    return e != 5 and e != 6    # not saturday and not sunday


###################################################


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

