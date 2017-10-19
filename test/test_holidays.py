import unittest

from corr.holidays import (
    trading_dates,
)


class TestHolidays(unittest.TestCase):

    def test_trading_dates(self):
        self.assertEqual(list(trading_dates('2017-10-01', '2017-10-07')), ['2017-10-02', '2017-10-03', '2017-10-04', '2017-10-05', '2017-10-06'])
        self.assertEqual(list(trading_dates('2017-11-19', '2017-11-25')), ['2017-11-20', '2017-11-21', '2017-11-22', '2017-11-24'])
        self.assertEqual(list(trading_dates('2017-12-24', '2017-12-30')), ['2017-12-26', '2017-12-27', '2017-12-28', '2017-12-29'])


if __name__ == '__main__':
    unittest.main()
