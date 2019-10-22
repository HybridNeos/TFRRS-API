from AthleteTfrrs import Athlete, Athlete
import unittest

class TestTfrrsApi(unittest.TestCase):

    #With invalid arguments should raise an exception
    def test_urlException(self):
        try:
            Test1 = Athlete("60924888", "Nowhere", "No one")
            self.assertEqual(1, 2)
        except:
            self.assertEqual(1, 1)

    #With all arguments check for correct url, no exception, and HTML loaded
    def test_urlAllArguments(self):
        try:
            Test2 = Athlete("6092422", "RPI", "Mark Shapiro")
            self.assertEqual(Test2.url, "https://www.tfrrs.org/athletes/6092422/RPI/Mark_Shapiro.html")
            self.assertTrue(Test2.HTML)
        except:
            self.assertEqual(1, 2)

    def test_urlJustId(self):
        try:
            Test3 = Athlete("6092422")
            self.assertTrue(Test3.HTML)
        except:
            self.assertEqual(1, 2)

if __name__ == '__main__':
    unittest.main()
