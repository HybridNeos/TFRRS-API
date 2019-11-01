from AthleteTfrrs import Athlete
import unittest
import json
from concurrent.futures import ThreadPoolExecutor

class TestTfrrsApi(unittest.TestCase):

    # Override tests
    def __init__(self, *args, **kwargs):
        super(TestTfrrsApi, self).__init__(*args, **kwargs)

        # Get athletes for tests
        IDs = ["6092422", "6092256", "5997832", "6092450"]
        with ThreadPoolExecutor(max_workers=len(IDs)) as executor:
            athletes = []
            for result in executor.map(Athlete, IDs):
                athletes.append(result)
            self.Mark, self.Pat, self.Skender, self.Zaire = athletes

    # Make sure an exception is raised with invalid arguments
    def test_urlException(self):
        self.assertRaises(Exception, Athlete, ("694201337"))
        self.assertRaises(Exception, Athlete, ("6092422", "No where"))
        self.assertRaises(Exception, Athlete, ("6092422", "RPI", "No one"))

    def test_urlAllArguments(self):
        # Make sure it works with all three configurations
        try:
            Test1 = Athlete("6092422")
            Test2 = Athlete("6092422", "RPI")
            Test3 = Athlete("6092422", "RPI", "Mark Shapiro")
            Test4 = Athlete("6092422", None, "Mark Shapiro")
        except Exception as e:
            raise e

    def test_getAthleteInfo(self):
        # Standard case
        self.assertEqual(
            self.Mark.getAthleteInfo(),
            json.dumps(
                {
                    "Name": "Mark Shapiro",
                    "Grade": "JR", "Year": 3,
                    "School": "RPI"
                },
                indent=4,
            ),
        )

        # Redshirt special case
        self.assertEqual(
            self.Alex.getAthleteInfo(),
            json.dumps(
                {
                    "Name": "Alex Skender",
                    "Grade": "Redshirt",
                    "Year": "Unattached",
                    "School": "RPI",
                },
                indent=4,
            ),
        )

        # TODO: Get a GR grade and handle graduates test case

    def test_getPRs(self):
        # Throws test
        self.assertEqual(
            self.Mark.getPersonalRecords(),
            json.dumps(
                {
                    "SP": 15.38,
                    "DT": 46.96,
                    "HT": 51.19,
                    "WT": 17.42
                },
                indent=4
            ),
        )

        # Jumps/sprints test
        self.assertEqual(
            self.Zaire.getPersonalRecords(),
            json.dumps(
                {
                    "60": 7.14,
                    "100": 11.22,
                    "200": 23.90,
                    "HJ": 1.76,
                    "LJ": 6.57
                },
                indent=4,
            ),
        )

        # Distance/xc test
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
            ),
        )


if __name__ == "__main__":
    unittest.main()
