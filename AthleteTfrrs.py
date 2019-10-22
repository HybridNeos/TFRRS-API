import pandas as pd
import requests
import json
import re
from collections import OrderedDict
from numpy import empty
from bs4 import BeautifulSoup

class Athlete:
    def __init__(self, ID, school="", name=""):
        # Make the URL
        url = "https://www.tfrrs.org/athletes/" + ID + "/"
        if school:
            url += school + "/"
        if name:
            url += name.replace(" ", "_") + ".html"

        # Get the response
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        # Handle the response
        if response.status_code < 300 and response.status_code >= 200:
            # panda's read_html doesn't accept percent colspan arguments
            self.HTML = response.text.replace('colspan="100%"', 'colspan="3"')

        else:
            self.HTML = None
            raise Exception("Could not retrieve", response.status_code)

    def parse(self):
        if self.HTML:
            # Setup
            dfs = pd.read_html(self.HTML)
            self.data = OrderedDict()
            self.soup = BeautifulSoup(self.HTML, "html5lib")

            # Get athlete info
            self.getAthleteInfo()

            # PRs
            self.parsePersonalRecords(dfs[0])

            # Meet results
            self.parseMeetResults(dfs[1:])

            # Return
            return json.dumps(self.data, indent=4)

        else:
            raise Exception("No HTML loaded. Retry with a different ID")

    def getMeetIds(self):
        links = self.soup.find_all("a")
        IDs = []

        # Pull the meet ID from href URLs
        for link in links:
            if re.search('href="//www.tfrrs.org/results/\d{5,6}/\w+_', str(link)):
                link = str(link)
                idStart = re.search("/results/\d{5,6}/", link).start() + len(
                    "/results/"
                )
                IDs += [link[idStart : idStart + 5]]

        return IDs

    def notCrossCountry(self, df):
        return "K" not in str(df.iloc[0, 0])

    def parseOneMeet(self, df, ID):
        # Get meet name and date
        dateStart = re.search(self.dateRegex, df.columns[0]).start()
        Meet = df.columns[0][:dateStart].rstrip()
        Date = df.columns[0][dateStart:]
        startDate, endDate = self.parseDates(Date)

        # JSON the meet info
        meetInfo = OrderedDict()
        meetInfo["Meet Name"] = Meet
        meetInfo["Start Date"] = startDate
        meetInfo["End Date"] = endDate

        # Add a column and rename columns
        df = pd.concat(
            [df, pd.DataFrame(empty([df.shape[0], 1], dtype=object))], axis=1
        )
        df.columns = ["Event", "Mark", "Place", "Round"]

        # Settle columns
        df["Mark"] = df["Mark"].apply(
            lambda mark: self.parseEventMark(
                df["Event"][df[df["Mark"] == mark].index.item()], mark
            )
        )
        df["Place"] = df["Place"].fillna("N/A")
        df["Round"] = [
            "F" if "(F)" in row else ("P" if "(P)" in row else "N/A")
            for row in df["Place"]
        ]
        df["Place"] = [
            row if row == "N/A" else row[0 : len(row) - 4] for row in df["Place"]
        ]
        df.set_index("Event", inplace=True)
        df.index = [str(event) for event in df.index]

        # JSON to meet results
        meetInfo["Results"] = OrderedDict()
        for i in range(0, df.shape[0]):
            meetInfo["Results"][df.index[i]] = df.iloc[i, :].to_list()

        # add into data
        self.data["Meet Results"][ID] = meetInfo

    def parseMeetResults(self, dfs):
        # Setup
        self.data["Result Format"] = "Event: [Mark, Place, Round]"
        self.data["Meet Results"] = OrderedDict()

        # Since more than meet results are read in, use regex to determine when they stop
        self.dateRegex = "[A-Z][a-z]{2} \d{1,2}(-\d{1,2}){0,1},"
        firstNonResult = [
            True if (re.search(self.dateRegex, df.columns[0])) else False
            for df in dfs[1:]
        ].index(False) + 1

        # Get the meet IDs ahead of time and pass that to the JSON creating function
        IDs = self.getMeetIds()
        i = 0

        # Loop
        for df in dfs[1:firstNonResult]:
            if self.notCrossCountry(df):
                self.parseOneMeet(df, IDs[i])
                i += 1

    def getAthleteInfo(self):
        # Use beautifulsoup to find the proper section and extract the text
        athleteInfo = (
            self.soup.find("div", class_="panel-heading")
            .get_text()
            .replace("\n", "")
            .strip()
        )
        athleteInfo = " ".join(athleteInfo.split())
        athleteInfo = athleteInfo.replace("RED SHIRT", "REDSHIRT")

        # Format the text into a usable list
        athleteInfo = athleteInfo.split()
        athleteInfo[0] = athleteInfo[0] + " " + athleteInfo[1]
        grade, year = (
            athleteInfo[2].split("/")
            if "REDSHIRT" in athleteInfo[2]
            else athleteInfo[2].split("-")
        )
        athleteInfo[1] = grade[1:]
        athleteInfo[2] = year[:-1]

        # Put it into data
        self.data["Name"] = athleteInfo[0]
        self.data["Grade"] = athleteInfo[1]
        self.data["Year"] = athleteInfo[2]
        self.data["School"] = athleteInfo[3]

    def parseDates(self, Date):
        if "/" in Date:

            def chunkToFormat(chunk):
                month, day = chunk.split("/")
                numToMonth = {
                    "01": "Jan",
                    "02": "Feb",
                    "03": "Mar",
                    "04": "Apr",
                    "05": "May",
                    "06": "Jun",
                    "07": "Jul",
                    "08": "Aug",
                    "09": "Sep",
                    "10": "Oct",
                    "11": "Nov",
                    "12": "Dec",
                }
                month = numToMonth[month]
                return month + " " + day

            dashIndex = Date.index("-")
            year = Date[-4:]
            chunk = Date[: dashIndex - 1]
            return chunkToFormat(chunk) + ", " + year, Date[dashIndex + 2 :]

        elif "-" in Date:
            Month = Date[: Date.index(" ")]
            Year = Date[-4:]
            Days = Date.split(" ")[1].replace(",", "").split("-")
            return (
                Month + " " + Days[0] + ", " + Year,
                Month + " " + Days[1] + ", " + Year,
            )

        else:
            return Date, Date

    def parseEventMark(self, eventType, mark):
        if eventType in ["SP", "DT", "HT", "WT", "JT", "LJ", "TJ"]:
            return mark if mark.isalpha() else mark.split(" ")[0]
        else:
            return mark

    def parsePersonalRecords(self, df):
        # Create the np array to fill in
        numLeft = sum(pd.notnull(df.iloc[:, 0]))
        numRight = sum(pd.notnull(df.iloc[:, 2]))
        numEvents = numLeft + numRight
        PRs = empty([numEvents, 2], dtype=object)

        # Fill in the array
        for i in range(0, df.shape[0]):
            PRs[i, 0] = df.iloc[i, 0]
            PRs[i, 1] = df.iloc[i, 1]

            if pd.notnull(df.iloc[i, 2]):
                PRs[i + numLeft, 0] = df.iloc[i, 2]
                PRs[i + numLeft, 1] = df.iloc[i, 3]

        # Convert to dataframe
        PRs = pd.DataFrame(PRs)
        PRs.columns = ["Event", "Mark"]

        # Clean up the dataframe
        PRs["Mark"] = PRs["Mark"].apply(
            lambda mark: self.parseEventMark(
                PRs["Event"][PRs[PRs["Mark"] == mark].index.item()], mark
            )
        )

        # Remove XC PRs
        PRs.set_index("Event", inplace=True)
        XC = list(filter(lambda event: "XC" in event, PRs.index))
        PRs.drop(XC, inplace=True)

        # Put it into data
        #   ["Mark"] used since column name persists
        self.data["College Bests"] = PRs.to_dict()["Mark"]

def AthleteTfrrs(ID, School=None, Name=None):
    AthleteResults = Athlete(ID, School, Name)
    return AthleteResults.parse()

if __name__ == "__main__":
    # Test = AthleteTfrrs("6092422", "RPI", "Mark Shapiro")
    # Test = AthleteTfrrs("6092256", "RPI", "Patrick Butler")
    Test = AthleteTfrrs("5997832", "RPI", "Alex Skender")
    print(Test)
