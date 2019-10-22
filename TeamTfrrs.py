import pandas as pd
import requests
import json
import re
from collections import OrderedDict
from bs4 import BeautifulSoup
from AthleteTfrrs import AthleteTfrrs

class Team:
    def __init__(self, State, Gender, Name):
        # Construct the url and make the request
        url_stub = "http://www.tfrrs.org/teams/"+State+"_college_"+Gender.lower()+"_"+Name
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"
        }
        response = requests.get(url_stub, headers=headers)

        # If the reponse succeeded
        if response.status_code < 300 and response.status_code >= 200:
            # panda's read_html doesn't accept percent colspan arguments
            self.HTML = response.text.replace('colspan="100%"', 'colspan="3"')
        # If the response failed
        else:
            self.HTML = None
            raise Exception("Could not retrieve", response.status_code)

    def parse(self):
        if self.HTML:
            # Setup
            dfs = pd.read_html(self.HTML)
            self.data = OrderedDict()
            self.soup = BeautifulSoup(self.HTML, "html5lib")
            

        else:
            raise Exception("No HTML loaded. Retry with a different information")

def TeamTfrrs(State, Gender, Name):
    TeamResults = Team(State, Gender, Name)
    return TeamResults.parse()

if __name__ == "__main__":
    Test = TeamTfrrs("NY", "M", "RPI")
