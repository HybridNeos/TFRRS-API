import pandas as pd
import requests

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"}
    response = requests.get("https://www.tfrrs.org/athletes/6092422/RPI/Mark_Shapiro.html", headers=headers)
    
    if response.status_code < 400 and response.status_code >= 200:
        HTML = response.text.replace("colspan=\"100%\"", "colspan=\"3\"")
        dfs = pd.read_html(HTML, header=0)
        cleanupDataframe(dfs[1])

    else:
        print("Error {} occured".format(response.status_code))

def cleanupDataframe(df):
    Meet, Date = df.columns[0].split("  ")
    print(Meet)
    print(Date)

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
    
    print(df)

if __name__ == '__main__':
    main()