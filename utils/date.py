from datetime import datetime, timedelta

def datestr_to_epoch(datestr, fmt='%Y-%m-%d'):
    dt = datetime.strptime(datestr, fmt)
    return dt.strftime('%s')

def datestr_offset(datestr, inc=1, fmt='%Y-%m-%d'):
    dt = datetime.strptime(datestr, fmt)
    dt += timedelta(days=inc)
    return dt.strftime(fmt)





def test_datestr_to_epoch():
    print(datestr_to_epoch('20101111', fmt='%Y%m%d'))
    print(datestr_to_epoch('1970-01-01'))

def test_datestr_offset():
    print(datestr_offset('2010-01-01'))
    print(datestr_offset('2010-01-01', -1))
    print(datestr_offset('2010-12-31'))
    print(datestr_offset('2010-12-31', -1))

def test():
    test_datestr_to_epoch()
    test_datestr_offset()

if __name__ == '__main__':
    test()
