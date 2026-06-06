import json
import pandas as py
from pathlib import Path
import csv
import requests
import zipfile
import io
import psycopg2
import psycopg2.extras

#Path for the data with all JSON files of the matches

#directory_path = Path("Data")

#Creates a df for each match, df holds general match data
def createMetadata(data, match_id):

    #Extract each attr from JSON to dict
    info = data.get("info", {})

    #Start and End Dates
    dates = info.get('dates', [])
    if dates:
        if len(dates) == 1:
            StartDate = EndDate = dates[0]
        else:
            StartDate = dates[0]
            EndDate = dates[-1]

    #Event object of info
    event = info.get("event", {})


    #Get officials and return their personID to the Dict
    officials = info.get("officials", {})
    registry = info.get("registry", {}).get("people", {})

    def get_person_id(name):
        return registry.get(name) if name else None

    match_refs = officials.get("match_referees", [])
    MatchRef = get_person_id(match_refs[0]) if match_refs else None

    tv_umpires = officials.get("tv_umpires", [])
    TVUmpire = get_person_id(tv_umpires[0]) if tv_umpires else None

    umpires = officials.get("umpires", [])
    Umpire1 = get_person_id(umpires[0]) if len(umpires) > 0 else None
    Umpire2 = get_person_id(umpires[1]) if len(umpires) > 1 else None

    winner = info.get("outcome", {}).get("winner")

    if winner:
        matchOutcome = "win"
        matchWinner = winner
        margin = info.get("outcome", {}).get("by",{})

        if margin.get("runs",""):
            winMargin = "by " + str(margin.get("runs","")) + " runs"
        else:
            winMargin = "by " + str(margin.get("wickets","")) + " wickets"
    else:
        matchWinner = None
        winMargin = None
        matchOutcome = info.get("outcome", {}).get("result")

        


    potm = info.get("player_of_match", [])


    teams = info.get("teams", [])
    team_1 = teams[0] if len(teams) > 0 else None
    team_2 = teams[1] if len(teams) > 1 else None

    toss = info.get("toss", {})


    return{
        'MatchID': match_id,
        'StartDate': StartDate,
        'EndDate': EndDate,
        'EventName': event.get("name"),
        'EventMatchNumber': event.get("match_number"),
        'Gender': info.get("gender"),
        'Format': info.get("match_type"),
        'MatchRef': get_person_id(match_refs[0]) if match_refs else None,
        'TVUmpire': get_person_id(tv_umpires[0]) if tv_umpires else None,
        'Umpire1': get_person_id(umpires[0]) if len(umpires) > 0 else None,
        'Umpire2': get_person_id(umpires[1]) if len(umpires) > 1 else None,
        'Winner': matchWinner,
        'WinMargin': winMargin,
        'Outcome': matchOutcome,
        'POTM': potm[0] if potm else None,
        'TeamType': info.get("team_type"),
        'Team1': team_1,
        'Team2': team_2,
        'TossWinner': toss.get("winner"),
        'TossDecision': toss.get("decision"),
        'Venue': info.get("venue"),
        'City': info.get("city")
    }


def addDeliveries(data,match_id):
    innings = data.get("innings", [])
    rows = []
    for inningIdx,i in enumerate(innings):
        inningNum = inningIdx+1
        battingTeam = i.get("team","")
        overs = i.get("overs",[])

        for o in overs:
            ovrNum = o.get("over",None)
            deliveries = o.get("deliveries",[])
            
            for delIdx,d in enumerate(deliveries):
                ballNum = delIdx+1

                runs = d.get("runs",{})
                runsBatter = runs.get("batter",0)
                runsExtras = runs.get("extras",0)

                extras = d.get("extras", {})

                if extras:
                    extra_type = next(iter(extras.keys()), None)
                else: 
                    extra_type = None

                wickets = d.get("wickets",[])
                fielder = None

                if len(wickets) > 0:
                    wicketFell = True
                    playerOut = wickets[0].get("player_out")
                    dismissalType = wickets[0].get("kind")
                    if wickets[0].get("fielders",[]):
                        fielder =  wickets[0].get("fielders",[])[0].get("name","")

                else:
                    wicketFell = False
                    playerOut = None
                    dismissalType = None
                    fielder = None



                row = {
                    'MatchID': match_id,
                    'InningsNum': inningNum,
                    'OverNum': ovrNum,
                    'BallNum': ballNum,
                    'Batter': d.get("batter"),
                    'Bowler': d.get("bowler"),
                    'NonStriker': d.get("non_striker"),
                    'RunsBatter': runsBatter,
                    'RunsExtras': runsExtras,
                    'ExtraType': extra_type,
                    'WicketFell': wicketFell,
                    'PlayerOut': playerOut,
                    'DismissalType': dismissalType,
                    'fielder': fielder
                }
                rows.append(row)
            
    return rows


def load_people_dict(csv_path):
    people_dict = {}
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            identifier = row.get('identifier')
            name = row.get('name')
            if identifier:
                people_dict[identifier] = name
    return people_dict

def loadMatches(data, match_id):
    match_players = []
    players = data.get("info", {}).get("players", {})
    registry = data.get("info", {}).get("registry", {}).get("people", {})

    teams = list(players.keys())

    team1 = teams[0] if len(teams) > 0 else None
    team2 = teams[1] if len(teams) > 1 else None

    if team1:
        for p in players[team1]:
            player_id = registry.get(p)
            match_players.append({
                'MatchID': match_id,
                'PlayerID': player_id,
                'Team': team1
            })

    if team2:
        for p in players[team2]:
            player_id = registry.get(p)
            match_players.append({
                'MatchID': match_id,
                'PlayerID': player_id,
                'Team': team2
            })

    return match_players

def getData():
    matchMetadata = []
    balls = []
    matchPlayers = []

    #Create people dict 
    peopleCSVPath = Path("Registry/people.csv")
    try:
        people_dict = load_people_dict(peopleCSVPath)
    except Exception:
        people_dict = {}

    url = "https://cricsheet.org/downloads/all_json.zip"
    print("Downloading all match data zip file from Cricsheet (approx. 100MB)...")
    
    #Try to virtually download the data
    try:
        #Get the zip folder and loop through each JSON in the zipped dir
        response = requests.get(url, stream=True)
        response.raise_for_status()  
        total_length = response.headers.get('content-length')
        zip_memory = io.BytesIO()

        if total_length is None:
            zip_memory.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            last_reported = -5
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                if chunk:
                    dl += len(chunk)
                    zip_memory.write(chunk)
                    percent = int(100 * dl / total_length)
                    if percent >= last_reported + 5:
                        print(f"Download Progress: {percent}% ({dl // (1024 * 1024)}MB / {total_length // (1024 * 1024)}MB)")
                        last_reported = percent

        zip_memory.seek(0)
        print("Download completed! Unzipping and parsing JSON files...")

        with zipfile.ZipFile(zip_memory) as archive:
            for file_name in archive.namelist():

                if file_name.endswith('.json'):

                    match_id = str(file_name)[:-5]
                    with archive.open(file_name) as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            print(f"Warning: Skipping empty or corrupt file: {file_name}")
                            continue

                        #add metadata
                        matchMetadata.append(createMetadata(data, match_id))
                        #add balls
                        balls.extend(addDeliveries(data, match_id))
                        #add match players
                        matchPlayers.extend(loadMatches(data, match_id))

                        # Add registry names to people_dict
                        registry = data.get("info", {}).get("registry", {}).get("people", {})
                        for name, pid in registry.items():
                            if pid and pid not in people_dict:
                                people_dict[pid] = name

                        print( "ID:" + str(match_id) + " done" )

    #If file doesnt open
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}") 
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

    return matchMetadata, balls, matchPlayers, people_dict
 
def exportData(matchMetadata, balls, matchPlayers, people_dict):

    createTables = """
        CREATE TABLE IF NOT EXISTS matches (
            match_id VARCHAR(50) PRIMARY KEY,
            start_date DATE,
            end_date DATE,
            event_name VARCHAR(100),
            event_match_number INT,
            gender VARCHAR(20),
            format VARCHAR(20),
            match_ref VARCHAR(50),
            tv_umpire VARCHAR(50),
            umpire_1 VARCHAR(50),
            umpire_2 VARCHAR(50),
            winner VARCHAR(50),
            win_margin VARCHAR(50),
            outcome VARCHAR(50),
            potm VARCHAR(50),
            team_type VARCHAR(20),
            team_1 VARCHAR(100),
            team_2 VARCHAR(100),
            toss_winner VARCHAR(100),
            toss_decision VARCHAR(10),
            venue VARCHAR(250),
            city VARCHAR(100)
        );

        CREATE TABLE IF NOT EXISTS players (
            player_id VARCHAR(50) PRIMARY KEY,
            player_name VARCHAR(150)
        );

        CREATE TABLE IF NOT EXISTS deliveries (
            match_id VARCHAR(50) REFERENCES matches(match_id),
            innings_no INT,
            over_no INT,
            ball_no INT,
            batter VARCHAR(100),
            bowler VARCHAR(100),
            non_striker VARCHAR(100),
            runs_batter INT,
            runs_extras INT,
            extra_type VARCHAR(20),
            wicket_fell BOOLEAN,
            player_out VARCHAR(100),
            dismissal_kind VARCHAR(50),
            fielder VARCHAR(50),
            PRIMARY KEY (match_id, innings_no, over_no, ball_no)
        );

        CREATE TABLE IF NOT EXISTS match_to_players (
            match_id VARCHAR(50) REFERENCES matches(match_id),
            player_id VARCHAR(50) REFERENCES players(player_id),
            team_name VARCHAR(100),
            PRIMARY KEY (match_id, player_id)
        );
        """
    insertMatches = """
        INSERT INTO matches (
            match_id,start_date,end_date,event_name,event_match_number,gender,
            format,match_ref,tv_umpire,umpire_1,umpire_2,winner,win_margin,
            outcome,potm,team_type,team_1,team_2,toss_winner,toss_decision,
            venue,city
        ) VALUES %s
        ON CONFLICT (match_id) DO NOTHING
    """

    matchesTemplate = """(
        %(MatchID)s, %(StartDate)s, %(EndDate)s, %(EventName)s, %(EventMatchNumber)s,
        %(Gender)s, %(Format)s, %(MatchRef)s, %(TVUmpire)s, %(Umpire1)s, %(Umpire2)s,
        %(Winner)s, %(WinMargin)s, %(Outcome)s, %(POTM)s, %(TeamType)s, %(Team1)s, %(Team2)s,
        %(TossWinner)s, %(TossDecision)s, %(Venue)s, %(City)s
    )"""

    insertPlayers = """
        INSERT INTO players (player_id, player_name)
        VALUES %s
        ON CONFLICT (player_id) DO UPDATE SET player_name = EXCLUDED.player_name
    """

    playersTemplate = "(%(PlayerID)s, %(PlayerName)s)"

    insertMatchPlayers = """
        INSERT INTO match_to_players (match_id, player_id, team_name)
        VALUES %s
        ON CONFLICT (match_id, player_id) DO NOTHING
    """

    matchPlayersTemplate = "(%(MatchID)s, %(PlayerID)s, %(Team)s)"

    insertDeliveries = """
        INSERT INTO deliveries (
            match_id, innings_no, over_no, ball_no, batter, bowler, non_striker,
            runs_batter, runs_extras, extra_type, wicket_fell, player_out,
            dismissal_kind, fielder
        ) VALUES %s
        ON CONFLICT (match_id, innings_no, over_no, ball_no) DO NOTHING
    """

    deliveriesTemplate = """(
        %(MatchID)s, %(InningsNum)s, %(OverNum)s, %(BallNum)s, %(Batter)s, %(Bowler)s, %(NonStriker)s,
        %(RunsBatter)s, %(RunsExtras)s, %(ExtraType)s, %(WicketFell)s, %(PlayerOut)s,
        %(DismissalType)s, %(fielder)s
    )"""

    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            dbname="cricketDB",
            user="srikarrallapalli", 
            password=""              
        )
        cursor = conn.cursor()
        print("Connected with database")
        try:
            cursor.execute(createTables)
            conn.commit()
            print("Tables created successfully")

            # 1. Matches
            psycopg2.extras.execute_values(cursor, insertMatches, matchMetadata, template=matchesTemplate)
            conn.commit()
            print("Inserted matches metadata.")

            # 2. Players
            players_data = [{'PlayerID': pid, 'PlayerName': pname} for pid, pname in people_dict.items() if pid]
            if players_data:
                psycopg2.extras.execute_values(cursor, insertPlayers, players_data, template=playersTemplate)
                conn.commit()
                print(f"Inserted/updated {len(players_data)} players.")

            # 3. Match to players
            match_players_data = [mp for mp in matchPlayers if mp.get('PlayerID')]
            if match_players_data:
                psycopg2.extras.execute_values(cursor, insertMatchPlayers, match_players_data, template=matchPlayersTemplate)
                conn.commit()
                print(f"Inserted {len(match_players_data)} match-to-player mappings.")

            # 4. Deliveries
            if balls:
                psycopg2.extras.execute_values(cursor, insertDeliveries, balls, template=deliveriesTemplate)
                conn.commit()
                print(f"Inserted {len(balls)} deliveries.")

        except Exception as e:
            print(f"Database error occurred: {e}")
            conn.rollback()

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'conn' in locals():
            conn.rollback()

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("Database connection closed.")

    return 


if __name__ == '__main__':
    matchMetadata, balls, matchPlayers, people_dict = getData()
    print("Data loaded")
    exportData(matchMetadata, balls, matchPlayers, people_dict)
