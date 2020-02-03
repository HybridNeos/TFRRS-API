from TeamTfrrs import Team
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

    #def test_topMarks(self):
    #    pass

if __name__ == "__main__":
    unittest.main()
