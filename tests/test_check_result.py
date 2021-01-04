import unittest

from pytown_model.check import CheckResult


class CheckResult_test(unittest.TestCase):
    def setUp(self):
        self.check_result = CheckResult()

    def test_check_result(self):

        self.assertTrue(self.check_result)
        self.check_result += "Test1"
        self.assertFalse(self.check_result)
        self.assertEqual(self.check_result.msg, "Test1")
        self.check_result += "Test2"
        self.assertFalse(self.check_result)
        self.assertEqual(self.check_result.msg, "Test1\nTest2")
