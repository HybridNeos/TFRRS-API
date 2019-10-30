from AthleteTfrrs import Athlete, AthleteTfrrs
import unittest

class TestTfrrsApi(unittest.TestCase):

    #With invalid arguments should raise an exception
    def test_urlException(self):
        self.assertRaises(Exception, Athlete, ("60924888", "Nowhere", "No one"))

    #With that it can get html from all types (exception if failed)
    def test_urlAllArguments(self):
        Test1 = Athlete("6092422")
        Test2 = Athlete("6092422", "RPI")
        Test3 = Athlete("6092422", "RPI", "Mark Shapiro")

if __name__ == '__main__':
    unittest.main()
