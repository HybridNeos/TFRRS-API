import pandas as pd
import requests
import json
import re
from bs4 import BeautifulSoup
from AthleteTfrrs import Athlete


class Team:
    def __init__(self, State, Gender, Name):
        # Construct the url and make the request
        url_stub = "http://www.tfrrs.org/teams/{}_college_{}_{}".format(
            State, Gender.lower(), Name
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"
        }
        response = requests.get(url_stub, headers=headers)

        # If the reponse succeeded
        if response.status_code < 300 and response.status_code >= 200:
            # panda's read_html doesn't accept percent colspan arguments
            self.HTML = response.text.replace('colspan="100%"', 'colspan="3"')
            self.initialize()

        # If the response failed
        else:
            self.HTML = None
            raise Exception("Could not retrieve", response.status_code)

    def getAthleteIDs(self):
        # TODO: Append Athlete ID(s) to Top Marks
        links = self.soup.find_all("a")
        tempIDs = {}

        # Pull the athlete ID from href URLs
        for link in links:
            link = str(link)
            if "//www.tfrrs.org/athletes/" in link:
                link = link[34 : link.index(".html")]
                link = link.replace("__", "_")
                ID, school, name = link.split("/")
                first, last = name.split("_")
                name = last + ", " + first
                tempIDs[name] = ID

        # sort it since we had duplicates from top marks
        IDs = {}
        for item in sorted(tempIDs.items()):
            IDs[item[0]] = item[1]

        return IDs

    # MERGE Into meetIds, AthleteIds = self.getIDs() to reduce double soup.findl_all("a")
    # not working
    # breaks at Bates, RPI, MIT, Tufts
    def getMeetIds(self):
        links = self.soup.find_all("a")
        IDs = []

        # Pull the meet ID from href URLs
        for link in links:
            if re.search(
                'href="//www.tfrrs.org/results/(xc/){0,1}\d{5,6}/\w+(,|_)', str(link)
            ):
                link = str(link)
                idStart = re.search("/results/(xc/){0,1}\d{5,6}/", link).start() + len(
                    "/results/"
                )
                IDs += (
                    [link[idStart + 3 : idStart + 8]]
                    if "xc" in link
                    else [link[idStart : idStart + 5]]
                )

        return IDs

    def initialize(self):
        self.dfs = pd.read_html(self.HTML)
        self.soup = BeautifulSoup(self.HTML, "html5lib")
        self.AthleteIDs = self.getAthleteIDs()
        self.MeetIDs = self.getMeetIds()

        return None

    def getAll(self):
        if self.HTML:
            # Setup
            data = {}
            data["Roster"] = self.getRoster()
            data["Latest Results"] = self.getLatestResults()
            data["Top Marks"] = self.getTopMarks()
            return data

        else:
            raise Exception("No HTML loaded. Retry with different information")

    def getRoster(self, asDict=False):
        Roster = self.dfs[1]
        RosterIDs = pd.Series(
            [self.AthleteIDs[name] for name in Roster["NAME"].to_list()]
        )
        # Append IDs to roster
        Roster = pd.concat([Roster, RosterIDs.rename("Athlete ID")], axis=1)

        return Roster.to_dict() if asDict else Roster

    def getLatestResults(self, asDict=False):
        LatestResults = self.dfs[2]
        MeetIDs = pd.Series(self.MeetIDs)
        # Append Meet IDs to results
        LatestResults = pd.concat((LatestResults, MeetIDs.rename("Meet ID")), axis=1)

        return LatestResults.to_dict() if asDict else LatestResults

    def getTopMarks(self, asDict=False):
        TopMarks = self.dfs[0]
        MarkIDs = pd.Series(
            [
                self.AthleteIDs[name] if name in self.AthleteIDs.keys() else None
                for name in TopMarks["ATHLETE/SQUAD"]
            ]
        )
        # Append Athlete IDs to top marks
        TopMarks = pd.concat((TopMarks, MarkIDs.rename("Athlete ID")), axis=1)

        return TopMarks.to_dict() if asDict else TopMarks


if __name__ == "__main__":
    Test = Team("NY", "F", "RPI")
    print(Test.getRoster())
