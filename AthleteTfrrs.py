import pandas as pd
import requests
import json
import re
import numpy as np
from bs4 import BeautifulSoup


def parseEventMark(mark):
    # try to make pandas use float to avoid importing all of numpy
    if isinstance(mark, np.float64) or isinstance(mark, float):
        return float(mark)

    # Some results are just the float
    if mark.isalpha():
        return mark

    # Possible edge case - false start with wind
    if "FS" in mark:
        return "FS"

    # possibly irrelevant
    elif mark.replace(".", "").isnumeric():
        return float(mark)

    else:
        # Don't want feet conversion or wind right now
        endChars = ["m", "W", "w", "(", "W"]
        for char in endChars:
            if char in mark:
                return float(mark[0 : mark.index(char)])

    # Unaccounted for
    return mark


def parseEventName(name):
    cleaned = str(name).replace("  ", " ") if name != "10000" else "10,000"
    return cleaned.replace(".0", "")


class Athlete:
    def __init__(self, ID, school="", name=""):
        # Make the URL
        url = "https://www.tfrrs.org/athletes/" + ID + "/"
        if school:
            url += school + "/"
        if name:
            url += name.replace(" ", "_")

        # Get the response
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        # Create the attributes and leave them blank
        self.data = None
        self.soup = None
        self.dfs = None

        # Handle the response
        if response.status_code < 300 and response.status_code >= 200:
            # panda's read_html doesn't accept percent colspan arguments
            self.HTML = response.text.replace('colspan="100%"', 'colspan="3"')
        else:
            self.HTML = None
            raise Exception("Could not retrieve", response.status_code)

    def getAthleteInfo(self):
        if not self.soup:
            self.soup = BeautifulSoup(self.HTML, "html5lib")

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
        return {
            "Name": athleteInfo[0],
            "Grade": athleteInfo[1],
            "Year": int(athleteInfo[2])
            if athleteInfo[2].isnumeric()
            else athleteInfo[2],
            "School": athleteInfo[3],
        }

    def getPersonalRecords(self):
        # If not created already get the dataframes
        if not self.dfs:
            self.dfs = pd.read_html(self.HTML)
        # Check for no personal records
        if len(self.dfs) == 0:
            return {"Has not competed": None}
        df = self.dfs[0]

        # Create the np array to fill in
        numLeft = sum(pd.notnull(df.iloc[:, 0]))
        numRight = sum(pd.notnull(df.iloc[:, 2]))
        numEvents = numLeft + numRight
        PRs = np.empty([numEvents, 2], dtype=object)

        # Fill in the array
        for i in range(df.shape[0]):
            PRs[i, 0] = df.iloc[i, 0]
            PRs[i, 1] = df.iloc[i, 1]

            if pd.notnull(df.iloc[i, 2]):
                PRs[i + numLeft, 0] = df.iloc[i, 2]
                PRs[i + numLeft, 1] = df.iloc[i, 3]

        # Convert to dataframe
        PRs = pd.DataFrame(PRs)
        PRs.columns = ["Event", "Mark"]

        # Clean up the dataframe
        PRs["Mark"] = PRs["Mark"].apply(lambda mark: parseEventMark(mark))
        for i in range(len(PRs)):
            if PRs["Event"][i] in ("HEP", "PENT", "DEC"): # make this neater
                PRs["Mark"][i] = int(PRs["Mark"][i])
        PRs.set_index("Event", inplace=True)
        PRs.index = [parseEventName(event) for event in PRs.index]

        # Put it into data
        #   ["Mark"] used since column name persists
        return PRs.to_dict()["Mark"]

    def getAll(self):
        if self.HTML:
            # Setup
            data = self.getAthleteInfo()

            # Get athlete info
            data["Personal Records"] = self.getPersonalRecords()

            # Meet results
            data["Meet Results"] = self.getMeets()

            # Return
            return data

        else:
            raise Exception("No HTML loaded. Retry with a different ID")

    # TODO: Get XC ids and make sure everything is right
    def getMeetIds(self):
        if not self.soup:
            self.soup = BeautifulSoup(self.HTML, "html5lib")
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

    # REMOVE THIS
    def notCrossCountry(self, df):
        return "K" not in str(df.iloc[0, 0])

    def getOneMeet(self, df, ID):
        # Get meet name and date
        dateStart = re.search(self.dateRegex, df.columns[0]).start()
        Meet = df.columns[0][:dateStart].rstrip()
        Date = df.columns[0][dateStart:]
        startDate, endDate = self.parseDates(Date)

        # JSON the meet info
        meetInfo = {}
        meetInfo["Meet Name"] = Meet
        meetInfo["Start Date"] = startDate
        meetInfo["End Date"] = endDate

        # Add a column and rename columns
        df = pd.concat(
            [df, pd.DataFrame(np.empty([df.shape[0], 1], dtype=object))], axis=1
        )
        df.columns = ["Event", "Mark", "Place", "Round"]

        # Fix up the dataframe
        df["Mark"] = df["Mark"].apply(lambda mark: parseEventMark(mark))
        df["Place"] = df["Place"].fillna("N/A")

        # TODO // Clean this up if possible
        df["Round"] = [
            "F" if "(F)" in row else ("P" if "(P)" in row else "N/A")
            for row in df["Place"]
        ]

        def onlyNumber(place):
            # Remove last four digits (the round details) and take only digits
            number = ""
            for char in place[0:-4]:
                if not char.isalpha():
                    number += char
                else:
                    return int(number)

        df["Place"] = [row if row == "N/A" else onlyNumber(row) for row in df["Place"]]

        df.set_index("Event", inplace=True)
        df.index = [str(event) for event in df.index]

        # JSON to meet results
        meetInfo["Results"] = {}
        for i in range(0, df.shape[0]):
            meetInfo["Results"][df.index[i]] = df.iloc[i, :].to_list()

        # add into data
        return meetInfo

    def getMeets(self):
        if not self.dfs:
            self.dfs = pd.read_html(self.HTML)
        dfs = self.dfs[1:]

        # Since more than meet results are read in, use regex to determine when they stop
        self.dateRegex = "[A-Z][a-z]{2} \d{1,2}(-\d{1,2}){0,1},"
        firstNonResult = [
            True if (re.search(self.dateRegex, df.columns[0])) else False
            for df in dfs[1:]
        ].index(False) + 1

        # Get the meet IDs ahead of time and pass that to the JSON creating function
        IDs = self.getMeetIds()
        i = 0

        # Loop getting the meets
        meetData = {}
        for df in dfs[1:firstNonResult]:
            if self.notCrossCountry(df):
                meetData[IDs[i]] = self.getOneMeet(df, IDs[i])
                i += 1

        return meetData

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


if __name__ == "__main__":
    # Test = Athlete("6092422", "RPI", "Mark Shapiro")
    Test = Athlete("6092256", "RPI", "Patrick Butler")
    # Test = Athlete("5997832", "RPI", "Alex Skender")
    # Test = Athlete("6092450", "RPI", "Zaire Wilson")
    # Test = Athlete("6996057", "RPI", "Elizabeth Evans")
    # Test = Athlete("6092422", "RPI", "Mark Shapiro")

    Test.getMeets()
