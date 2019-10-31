from AthleteTfrrs import Athlete, AthleteTfrrs
import unittest

class TestTfrrsApi(unittest.TestCase):

    # Override tests
    def __init__(self, *args, **kwargs):
        super(TestTfrrsApi, self).__init__(*args, **kwargs)

    #With invalid arguments should raise an exception
    def test_urlException(self):
        self.assertRaises(Exception, Athlete, ("60924888", "Nowhere", "No one"))

    #With that it can get html from all types (exception if failed)
    def test_urlAllArguments(self):
        Test1 = Athlete("6092422")
        Test2 = Athlete("6092422", "RPI")
        Test3 = Athlete("6092422", "RPI", "Mark Shapiro")

    def test_canReadAll(self):
        # Pull in athletes to test with
        try:
            self.Mark = AthleteTfrrs("6092422", "RPI", "Mark Shapiro")
            self.Pat = AthleteTfrrs("6092256", "RPI", "Patrick Butler")
            self.Skender = AthleteTfrrs("5997832", "RPI", "Alex Skender")
            self.Zaire = AthleteTfrrs("6092450", "RPI", "Zaire Wilson")
            self.Liz = AthleteTfrrs("6996057", "RPI", "Elizabeth Evans")
        except Exception as e:
            raise e


if __name__ == '__main__':
    unittest.main()
