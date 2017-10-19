import unittest

from datetime import datetime

from corr.dateutils import (
    datestr_to_datetime,
    datestr_to_epoch,
    datestr_offset,
    idates,
    is_weekday,
    is_weekend,
)


class TestDateUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ##########################

    def test_datestr_to_datetime(self):
        self.assertEqual(datestr_to_datetime('20120101'), datetime(2012, 1, 1))
        self.assertEqual(datestr_to_datetime('2017-12-31'), datetime(2017, 12, 31))
        self.assertEqual(datestr_to_datetime('2008.09.30'), datetime(2008, 9, 30))
        self.assertIsNone(datestr_to_datetime('2008.09.31'))    # non-existent date, hence returns None
        self.assertIsNone(datestr_to_datetime('2017-12-34'))    # non-existent date, hence returns None

    def test_datestr_to_epoch(self):
        self.assertAlmostEqual(datestr_to_epoch('1970-01-01'), 0)

    def test_datestr_offset(self):
        self.assertEqual(datestr_offset('2010-01-01'), '2010-01-02')
        self.assertEqual(datestr_offset('20120304', -1), '20120303')
        self.assertEqual(datestr_offset('20120304', -1, '%Y-%m-%d'), '2012-03-03')
        self.assertEqual(datestr_offset('2010-12-31'), '2011-01-01')
        self.assertEqual(datestr_offset('2010-12-31', -1), '2010-12-30')

    def test_idates(self):
        #     December 2010
        # Su Mo Tu We Th Fr Sa
        #           1  2  3  4
        #  5  6  7  8  9 10 11
        # 12 13 14 15 16 17 18
        # 19 20 21 22 23 24 25
        # 26 27 28 29 30 31
        self.assertEqual(list(idates('2010-12-22', '2010-12-25')), ['2010-12-22', '2010-12-23', '2010-12-24', '2010-12-25'])
        self.assertEqual(list(idates('20101201', '20101204')), ['20101201', '20101202', '20101203', '20101204'])
        self.assertEqual(list(idates('2010-12-10', '2010-12-13', predicate=is_weekday)), ['2010-12-10', '2010-12-13'])
        self.assertEqual(list(idates('2010-12-10', '2010-12-13', predicate=is_weekend)), ['2010-12-11', '2010-12-12'])

if __name__ == '__main__':
    unittest.main()
