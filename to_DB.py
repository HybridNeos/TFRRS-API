from TeamTfrrs import Team
from AthleteTfrrs import Athlete
import pscyopg2 as pg
from concurrent.futures import ThreadPoolExecutor

""" SPECIFIC TO RPI BUT CAN BE GENERALIZED """

# Get school
State = "NY"
School = "RPI"
RPI_Men = Team(State, "M", School).getRoster()
RPI_Women = Team(State, "F", School).getRoster()
IDs = list(RPI_Men["Athlete ID"].values) + list(RPI_Women["Athlete ID"].values)
Names = list(RPI_Men["NAME"].values) + list(RPI_Women["NAME"].values)

# Establish connection
toDB = False
if toDB:
    conn = pg.connect(
        "dbname='shapim' user='shapim' host='localhost' password='uhs2016rpi2020'"
    )
    cursor = conn.cursor()

    # Clear any previous
    cursor.execute("DELETE FROM athlete_info")
    cursor.execute("DELETE FROM athlete_events")

# Add to athlete_info
for i, name in enumerate(Names):
    Gender = "M" if i < len(RPI_Men) else "F"

    if toDB and conn:
        cursor.execute(
            "INSERT INTO athlete_info VALUES ('{}', '{}', '{}', '{}');".format(
                name.replace("'", "_"), State, Gender, School
            )
        )

# Get Event results
Athletes = []
with ThreadPoolExecutor(max_workers=len(IDs)) as executor:
    for result in executor.map(Athlete, IDs):
        Athletes.append(result)

Events = [
    (name, list(athlete.getPersonalRecords().keys()))
    for name, athlete in zip(Names, Athletes)
]

# Add event results
for athlete in Events:
    if athlete[1] == "Has not competed":
        cursor.execute(
            "INSERT INTO athlete_events VALUES ('{}', '{}');".format(
                athlete[0].replace("'", "_"), NULL
            )
        )
    else:
        for PR in athlete[1]:
            cursor.execute(
                "INSERT INTO athlete_events VALUES ('{}', '{}');".format(
                    athlete[0].replace("'", "_"), PR
                )
            )

if toDB:
    conn.commit()
