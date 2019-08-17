import pandas as pd
import requests
from bs4 import BeautifulSoup

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"}
    response = requests.get("https://www.tfrrs.org/athletes/6092422/RPI/Mark_Shapiro.html", headers=headers)
    
    if response.status_code < 400 and response.status_code >= 200:
        HTML = response.text.replace("colspan=\"100%\"", "colspan=\"3\"")

        #Get athlete info
        info = getAthleteInfo(HTML)
        print(info)

        dfs = pd.read_html(HTML, header=0)
        cleanupDataframe(dfs[1])

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


def cleanupDataframe(df):
    Meet, Date = df.columns[0].split("  ")
    #print(Meet)
    #print(Date)

    #Add a column and rename columns
    finalOrPrelim = []
    for i in range(df.shape[0]):
        finalOrPrelim += "N"
    finalOrPrelim = pd.DataFrame(finalOrPrelim)
    
    df = pd.concat([df, finalOrPrelim], axis=1)
    df.columns = ["Event", "Mark", "Place", "Round"]

    #Settle columns
    df["Round"] = ["F" if "(F)" in row else "P" for row in df["Place"]]
    df["Place"] = [row[0:len(row)-4] for row in df["Place"]]
    df["Mark"]  = [row[0:row.index("m")] if "m" in row else row for row in df["Mark"]]
    
    print()
    print(df)

if __name__ == '__main__':
    main()