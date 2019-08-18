import pandas as pd
import requests
from numpy import arange
from bs4 import BeautifulSoup

class TfrrsApi:
    def __init__(self, ID, school="", name=""):
        self.url = "https://www.tfrrs.org/athletes/" + ID + "/" 
        if school:
            self.url += school + "/"
        if name:
            self.url += name.replace(" ", "_") + ".html"
        self.retrieve()

    def retrieve(self):
        #Make the request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"}        
        response = requests.get(self.url, headers=headers)    
        
        #Handle the response
        if response.status_code < 300 and response.status_code >= 200:
            #panda's read_html doesn't accept percent colspan arguments
            self.HTML = response.text.replace("colspan=\"100%\"", "colspan=\"3\"")

        else:
            self.HTML = ""
            raise Exception("Could not retrieve", response.status_code)

    def parse(self):
        if self.HTML:
            #Get athlete info
            info = self.getAthleteInfo()
            #print(info)

            #Get Personal Records
            PRs = self.getPersonalRecords()
            #print(PRs)

            #Get meet information
            dfs = pd.read_html(self.HTML, header=0)
            df = self.parseDataframe(dfs[1])
            #print(df)

        else:
            raise Exception("No HTML loaded")

    def getAthleteInfo(self):
        #Use beautifulsoup to find the proper section and extract the text
        soup = BeautifulSoup(self.HTML, "html5lib")
        athleteInfo = soup.find('div', class_="panel-heading").get_text().replace("\n", "").strip()
        athleteInfo = ' '.join(athleteInfo.split())
        
        #Format the text into a usable list
        athleteInfo = athleteInfo.split()
        athleteInfo[0] = athleteInfo[0] + " " + athleteInfo[1]
        grade, year = athleteInfo[2].split("-")
        athleteInfo[1] = grade[1:3]
        athleteInfo[2] = year[0:1]
        
        return athleteInfo

    def getPersonalRecords(self):
        return "Hi"

    def parseDates(self, Date):
        if "-" in Date:
            days = Date[Date.index(" ")+1:Date.index(",")]
            Date = Date.replace(days, "").split(",")
            return Date[0] + days.split("-")[0] + "," + Date[1], Date[0] + days.split("-")[1] + "," + Date[1]
        else:
            return Date, Date

    def parseDataframe(self, df):
        #Get meet information
        Meet, Date = df.columns[0].split("  ")
        startDate, endDate = self.parseDates(Date)

        #Add a column and rename columns    
        df = pd.concat([df, pd.DataFrame(arange(df.shape[0]).transpose())], axis=1)
        df.columns = ["Event", "Mark", "Place", "Round"]

        #Settle columns
        df["Round"] = ["F" if "(F)" in row else "P" for row in df["Place"]]
        df["Place"] = [row[0:len(row)-4] for row in df["Place"]]
        df["Mark"]  = [row[0:row.index("m")] if "m" in row else row for row in df["Mark"]]
        
        return df

if __name__ == '__main__':
    Test = TfrrsApi("6092422", "RPI", "Mark Shapiro")
    Test.parse()