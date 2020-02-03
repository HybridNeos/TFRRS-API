from TeamTfrrs import Team
from AthleteTfrrs import Athlete
import unittest
from concurrent.futures import ThreadPoolExecutor


class TestTfrrsApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        info = [("NY", "M", "RPI"), ("NY", "F", "RPI")]
        with ThreadPoolExecutor(max_workers=2) as executor:
            genders = []
            for result in executor.map(lambda params: Team(*params), info):
                genders.append(result)
        cls.Men, cls.Women = genders

    # Make sure both men and women have the correct number of athletes
    def test_numberOfAthletes(self):
        self.assertEqual(82, len(self.Men.getRoster()))
        self.assertEqual(52, len(self.Women.getRoster()))

    # def test_topMarks(self):
    #    pass

    def test_visuallyAllPersonalBests(self):
        show = True
        if show:
            print()
            IDs = list(self.Women.getRoster()["Athlete ID"].values)
            Names = list(self.Women.getRoster()["NAME"].values)

            Athletes = []
            with ThreadPoolExecutor(max_workers=len(IDs)) as executor:
                for result in executor.map(Athlete, IDs):
                    Athletes.append(result)

            personalBests = [
                {name: athlete.getPersonalRecords().keys()}
                for name, athlete in zip(Names, Athletes)
            ]
            for athlete in personalBests:
                for key in athlete:
                    print("{}\n{}\n".format(key, list(athlete[key])))


if __name__ == "__main__":
    unittest.main()
