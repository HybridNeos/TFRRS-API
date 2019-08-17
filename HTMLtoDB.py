import pandas as pd
import requests

def main():
    #try
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"}
    response = requests.get("https://www.tfrrs.org/athletes/6092422/RPI/Mark_Shapiro.html", headers=headers)
    
    if response.status_code < 400 and response.status_code >= 200:
        HTML = response.text.replace("colspan=\"100%\"", "colspan=\"3\"")
        dfs = pd.read_html(HTML)
    else:
        print("Error {} occured".format(response.status_code))

if __name__ == '__main__':
    main()