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

            # Get Athlete and Meet IDs to append to tables later
            self.AthleteIDs = self.getAthleteIDs()

            # Get the basic three tables
            self.getMainInformation(dfs)
            # TODO: add to internal df

            # TODO: Get region, more teams, season

        else:
            raise Exception("No HTML loaded. Retry with a different information")

    def getAthleteIDs(self):
        # TODO: Append Athlete ID(s) to Top Marks
        links = self.soup.find_all("a")
        tempIDs = {}

        # Pull the athlete ID from href URLs
        for link in links:
            link = str(link)
            if "//www.tfrrs.org/athletes/" in link:
                link = link[34:link.index(".html")]
                ID = link.split("/")[0]
                name = link.split("/")[2]
                first, last = name.split("_")
                name = last+", "+first
                tempIDs[name] = ID

        # sort it since we had duplicates from top marks
        IDs = {}
        for item in sorted(tempIDs.items()):
            IDs[item[0]] = item[1]

        return IDs

    def getMainInformation(self, dfs):
        # Pull out the tables
        TopMarks = dfs[0]
        Roster = dfs[1]
        LatestResults = dfs[2]

        #####IDS are wrong
        # Append Athlete ID to TopMarks
        MarkIDs = pd.Series([self.AthleteIDs[name] if name in self.AthleteIDs.keys() else None for name in TopMarks["ATHLETE/SQUAD"]])
        TopMarks = pd.concat((TopMarks, MarkIDs.rename("Athlete ID")), axis=1)
        print(TopMarks.head())

        # Append Athlete ID to Roster
        RosterIDs = pd.Series([self.AthleteIDs[name] for name in Roster["NAME"].to_list()])
        Roster = pd.concat([Roster, RosterIDs.rename("Athlete ID")], axis=1)

        # TODO: Append MeetId to LatestResults

def TeamTfrrs(State, Gender, Name):
    TeamResults = Team(State, Gender, Name)
    return TeamResults.parse()

if __name__ == "__main__":
    Test = TeamTfrrs("NY", "M", "RPI")
