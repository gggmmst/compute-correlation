import unittest

from corr.iterutils import (
    flatten,
)


class TestIterutils(unittest.TestCase):

    def test_flatten(self):
        self.assertEqual(flatten(((0,), (1,), (2, 3), (4, 5))), (0, 1, 2, 3, 4, 5))


if __name__ == '__main__':
    unittest.main()
