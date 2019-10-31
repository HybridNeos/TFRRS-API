from AthleteTfrrs import Athlete
import unittest
import json


class TestTfrrsApi(unittest.TestCase):

    # Override tests
    def __init__(self, *args, **kwargs):
        super(TestTfrrsApi, self).__init__(*args, **kwargs)

        # Get Information
        self.Mark = Athlete("6092422", "RPI", "Mark Shapiro")
        self.Pat = Athlete("6092256", "RPI", "Patrick Butler")
        self.Skender = Athlete("5997832", "RPI", "Alex Skender")
        self.Zaire = Athlete("6092450", "RPI", "Zaire Wilson")

    # With invalid arguments should raise an exception
    def test_urlException(self):
        self.assertRaises(Exception, Athlete, ("60924888", "Nowhere", "No one"))

    # With that it can get html from all types (exception if failed)
    def test_urlAllArguments(self):
        try:
            Test1 = Athlete("6092422")
            Test2 = Athlete("6092422", "RPI")
            Test3 = Athlete("6092422", "RPI", "Mark Shapiro")
        except Exception as e:
            raise e

    #def test_getAthleteInfo(self):


    def test_getPRs(self):
        self.assertEqual(
            self.Mark.getPersonalRecords(),
            json.dumps(
                {"SP": "15.38", "DT": "46.96", "HT": "51.19", "WT": "17.42"}, indent=4
            )
        )

        self.assertEqual(
            self.Zaire.getPersonalRecords(),
            json.dumps(
                {
                    "60": "7.14",
                    "100": "11.22",
                    "200": "23.90",
                    "HJ": "1.76",
                    "LJ": "6.57",
                },
                indent=4,
            )
        )

        self.assertEqual(
            self.Skender.getPersonalRecords(),
            json.dumps(
                {
                    "1500": "4:40.25",
                    "MILE": "4:49.62",
                    "3000": "9:18.27",
                    "5000": "15:26.67",
                    "10,000": "32:33.06",
                    "6K (XC)": "21:19.3",
                    "8K (XC)": "26:20.4",
                    "7.8K (XC)": "28:09.3",
                },
                indent=4,
            )
        )


if __name__ == "__main__":
    unittest.main()
