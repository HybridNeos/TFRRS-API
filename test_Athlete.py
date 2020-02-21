from AthleteTfrrs import Athlete
import unittest
import json
from concurrent.futures import ThreadPoolExecutor


class TestTfrrsApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        IDs = ["6092422", "6092256", "5997815", "6092450"]
        with ThreadPoolExecutor(max_workers=len(IDs)) as executor:
            athletes = []
            for result in executor.map(Athlete, IDs):
                athletes.append(result)
        cls.Mark, cls.Pat, cls.Noah, cls.Zaire = athletes

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
            {"60": 7.11, "100": 11.22, "200": 23.90, "HJ": 1.76, "LJ": 6.57},
        )

        # Distance/xc test
        self.assertEqual(
            self.Noah.getPersonalRecords(),
            {
                "800": "1:55.40",
                "1000": "2:34.79",
                "1500": "3:49.04",
                "MILE": "4:05.10",
                "3000": "8:18.67",
                "5000": "14:26.50",
                "6K (XC)": "20:27.8",
                "7.8K (XC)": "25:20.8",
                "8K (XC)": "24:55.5",
            },
        )

        multi = self.Pat.getPersonalRecords()
        self.assertEqual(
            multi,
            {
                "60": 7.27,
                "100": 11.42,
                "200": 23.54,
                "400": 50.21,
                "500": "1:08.56",
                "1000": "2:52.92",
                "1500": "4:40.11",
                "60H": 9.42,
                "110H": 17.24,
                "400H": 57.76,
                "HJ": 1.68,
                "PV": 2.95,
                "LJ": 6.91,
                "SP": 10.59,
                "DT": 30.20,
                "JT": 53.59,
                "HEP": 4192,
                "DEC": 5624,
            },
        )

        self.assertTrue(isinstance(multi["HEP"], int))
        self.assertTrue(isinstance(multi["DEC"], int))


if __name__ == "__main__":
    unittest.main()
