import pandas as pd
import requests
import re
from numpy import arange
from bs4 import BeautifulSoup

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"}
    response = requests.get("https://www.tfrrs.org/athletes/6092422/RPI/Mark_Shapiro.html", headers=headers)
    
    if response.status_code < 400 and response.status_code >= 200:
        HTML = response.text.replace("colspan=\"100%\"", "colspan=\"3\"")

        #Get athlete info
        info = getAthleteInfo(HTML)
        #print(info)

        #Get Personal Records
        PRs = getPersonalRecords(HTML)
        #print(PRs)

        #Get meet information
        dfs = pd.read_html(HTML, header=0)
        #parseDataframe(dfs[1])

    else:
        print("Error {} occured".format(response.status_code))

def getAthleteInfo(HTML):
    #Use beautifulsoup to find the proper section and extract the text
    soup = BeautifulSoup(HTML, "html5lib")
    athleteInfo = soup.find('div', class_="panel-heading").get_text().replace("\n", "").strip()
    athleteInfo = ' '.join(athleteInfo.split())
    
    #Format the text into a usable list
    athleteInfo = athleteInfo.split()
    athleteInfo[0] = athleteInfo[0] + " " + athleteInfo[1]
    grade, year = athleteInfo[2].split("-")
    athleteInfo[1] = grade[1:3]
    athleteInfo[2] = year[0:1]
    
    return athleteInfo

def getPersonalRecords(HTML):
    return "Hi"

def parseDates(Date):
    if "-" in Date:
        days = Date[Date.index(" ")+1:Date.index(",")]
        Date = Date.replace(days, "").split(",")
        return Date[0] + days.split("-")[0] + "," + Date[1], Date[0] + days.split("-")[1] + "," + Date[1]
    else:
        return Date, Date

def parseDataframe(df):
    #Get meet information
    Meet, Date = df.columns[0].split("  ")
    startDate, endDate = parseDates(Date)

    #Add a column and rename columns    
    df = pd.concat([df, pd.DataFrame(arange(df.shape[0]).transpose())], axis=1)
    df.columns = ["Event", "Mark", "Place", "Round"]

    #Settle columns
    df["Round"] = ["F" if "(F)" in row else "P" for row in df["Place"]]
    df["Place"] = [row[0:len(row)-4] for row in df["Place"]]
    df["Mark"]  = [row[0:row.index("m")] if "m" in row else row for row in df["Mark"]]
    
    #print(df)

if __name__ == '__main__':
    main()