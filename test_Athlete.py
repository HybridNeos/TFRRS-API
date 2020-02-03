from AthleteTfrrs import Athlete
import unittest
import json
from concurrent.futures import ThreadPoolExecutor


class TestTfrrsApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        IDs = ["6092422", "6092256", "5997832", "6092450"]
        with ThreadPoolExecutor(max_workers=len(IDs)) as executor:
            athletes = []
            for result in executor.map(Athlete, IDs):
                athletes.append(result)
        cls.Mark, cls.Pat, cls.Skender, cls.Zaire = athletes

    # Make sure an exception is raised with invalid arguments
    def test_urlException(self):
        self.assertRaises(Exception, Athlete, ("694201337"))
        self.assertRaises(Exception, Athlete, ("6092422", "No where"))
        self.assertRaises(Exception, Athlete, ("6092422", "RPI", "No one"))

    # Make sure it works with all three configurations
    def test_urlAllArguments(self):
        try:
            Test1 = Athlete("6092422")
            Test2 = Athlete("6092422", "RPI")
            Test3 = Athlete("6092422", "RPI", "Mark Shapiro")
            Test4 = Athlete("6092422", None, "Mark Shapiro")
        except Exception as e:
            raise e

    # Self explanatory
    def test_getAthleteInfo(self):
        # Standard case
        self.assertEqual(
            self.Mark.getAthleteInfo(),
            {"Name": "MARK SHAPIRO", "Grade": "SR", "Year": 4, "School": "RPI"},
        )

        # Was redshirt (it worked), now graduated
        self.assertEqual(
            self.Skender.getAthleteInfo(), {"Name": "ALEX SKENDER", "School": "RPI"}
        )

    # Self explanatory
    def test_getPRs(self):
        # Throws test
        self.assertEqual(
            self.Mark.getPersonalRecords(),
            {"SP": 15.38, "DT": 46.96, "HT": 51.19, "WT": 17.52},
        )

        # Jumps/sprints test
        self.assertEqual(
            self.Zaire.getPersonalRecords(),
            {"60": 7.14, "100": 11.22, "200": 23.90, "HJ": 1.76, "LJ": 6.57},
        )

        # Distance/xc test
        self.assertEqual(
            self.Skender.getPersonalRecords(),
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
        )


if __name__ == "__main__":
    unittest.main()
