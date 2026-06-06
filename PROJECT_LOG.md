# Project Log & Notes

## 05/11/26

### Project Idea
This project is a full-stack cricket analytics platform that uses historical match data with real-time scoring. It provides a web-based dashboard for player and team based statistics while utilizing an AI-driven analytical agent. The primary objective is to demonstrate a "grounded" AI architecture where a LLM performs deterministic analysis by querying a private relational database through tool-calling, rather than relying on probabilistic internal knowledge. This approach eliminates factual hallucinations and provides users with precise, up-to-date statistical insights. Overall, the app will provide basic stat website functionality (akin to CricBuzz, ESPN) and have this AI layer added on top of it.

### Technologies Needed
* **Front End:** ReactJS (via ViteJS), TailwindCSS
  * *To-do: Research more specific component libraries for neat graphs, plots, and such.*
* **Back End:** PostgreSQL, FastAPI
* **Cloud, Containerization, etc.:** AWS, Docker
* **Data Sources:** * Cricsheet (for in-depth historical data)
  * CricAPI (for live data)
  * *To-do: Look into other live APIs if possible.*

### First Steps & Learning Resources
* **FastAPI:** [Tutorial Link](https://www.youtube.com/watch?v=tLKKmouUams)
* **Git & Github:** [Tutorial Link](https://www.youtube.com/watch?v=mJ-qvsxPHpY)
* **Docker & Docker Compose:** [Tutorial Link](https://www.youtube.com/watch?v=3c-iBn73dDE)
* **AWS Concepts:** * [Video 1](https://www.youtube.com/watch?v=AYAh6YDXuho)
  * [Video 2](https://youtu.be/3hLmDS179YE?si=GdKHPgpsWVDZUszr)
* **Terraform & CICD via git:** [HashiCorp Tutorial](https://developer.hashicorp.com/terraform/tutorials/automation/github-actions)
* *Next Step: Plan out architecture.*

---

## 05/13/26

### Watched Tutorials
* **Git:** [Tutorial Link](https://www.youtube.com/watch?v=mJ-qvsxPHpY)

### Git Command Notes
| Command | Description |
| :--- | :--- |
| `git init` | Initialize project to use git |
| `git add .` | Add all changes to be saved |
| `git add <filename>` | Add single file to be saved |
| `git commit -m "message"` | Save changes with a message |
| `git push origin master` | Push changes to github master branch |
| `git push origin new-branch` | Push changes to github new-branch |
| `git pull origin master` | Pull changes from github master |
| `git checkout -b new-branch` | Create a new branch |
| `git status` | Check status of changes |
| `git log` | See all previous saved changes |
| `git checkout <commit hash>` | Travel back to old commit |

* **Docker:** [Tutorial Link](https://www.youtube.com/watch?v=pg19Z8LL06w)

---

## 05/20/26

### Plan for Data Transfer from Cricsheet to PostgreSQL

First I wanted to visualize the cricsheet data and understand its format.

  * The data is stored in JSON, where each JSON file represents one match.
    
  * In each file there are 3 main components:
    * Meta Object: contains metadata about the data file itself (date created, revision #, etc.)
    * Info Object: contains all the high-level details about the match (format, male or female, city, etc.)
    * Innings Array: This array contains 2 or 4 innings depending on format, each inning stores the ball-by-ball data, this array holds variables "team" (string), "declared" (boolean) and an array called overs:
        
      * The overs array contains the over number and the delivery array with objects (balls 1 to 6 of an over + extras if applicable).
        * Each delivary holds the following data:
          * Batsman and Non-Striker
          * Bowler
          * Runs (including data on batter runs scored and extras)
          * Extras (optional)
          * Wickets (optional): Which has data for kind of wicket, bowler and fielder (if applicable).


 After understanding the data, I wanted to figure out how I should store this data in SQL and do so efficiently. This step is critical if I want my website to be responsive later on. Before I can worry about the ball-by-ball stats, I need to create 2 master tables: one that stores basic player info (player name, date of birth, handedness, etc.) and another which stores match metadata (essentially the info object from the match JSON from cricsheet). 
 
 The problem here is that 22 players participate in one match. & A single player can play any n number of games. Causing a many to many relationship. 
 
 To solve this, I plan to add a seperate table which has one row for every match that every player has played:
 
| **MatchID** | **PlayerID** | **Country** |
| :--- | :--- | :--- |
| match_123 | player_A (Kohli) | India |
| match_123 | player_B (Rohit) | India |

... _for all 11 players for 2 teams (so 22 rows per match in total)_

This allows us to index by player and match which will make our analysis much more in-depth!

Lastly, we need a table that actually stores the ball-by-ball stats, each delivery will be assigned to a match id so we can index.

So we are able to index by match and player to obtain their ball-by-ball stats!

Now all that's left is to export the data into SQL!

## 06/04/26 

### Creating the database

Today's focus was creating the database and finalizing its functionalities. In order to make querying efficient, I had to first think of the use-cases for my DB and app as a whole.

I looked at various cricket analysis visualizations—such as worm graphs, partnership tables, Manhattan charts (runs per over), wagon wheels (scoring areas), and pitch maps (bowling lengths and lines). Analyzing how these graphics are generated made me realize that the two fundamental stats I need to search and aggregate by: **deliveries** and **players**.

Therefore, the core of the database relies on two main structures:

1. A ball-by-ball table: This provides the highest level of granularity. By storing data at the delivery level, the backend can easily aggregate the data upward by over, inning, or match to get higher-level stats on the fly.

2. A many-to-many player-to-matches table: This makes it highly efficient to query individual player statistics across specific timeframes or formats.

There are other things a user could query by such as venues, tournaments, etc. and adding specific tables for these would not be a bad idea, however I wanted to focus on the MVP for now. 

Below are the 4 main tables:

#### Table 1: matches (Metadata)

| **Column Name** | **SQL Type** | **Desc.** |
| :--- | :--- | :--- |
| `match_id` | VARCHAR(50) | Primary Key |
| `start_date` | DATE | Match start date |
| `end_date` | DATE | Match end date |
| `event_name` | VARCHAR(100) | Tournament/Series name |
| `event_match_number` | INT | Match number in series |
| `gender` | VARCHAR(10) | male/female |
| `format` | VARCHAR(10) | Test, ODI, T20, etc. |
| `match_ref` | VARCHAR(50) | Match Referee ID |
| `tv_umpire` | VARCHAR(50) | TV Umpire ID |
| `umpire_1` | VARCHAR(50) | On-field Umpire 1 ID |
| `umpire_2` | VARCHAR(50) | On-field Umpire 2 ID |
| `winner` | VARCHAR(50) | Winner (Name of winning team) |
| `win_margin` | VARCHAR(50) | Margin of victory by the winner (e.g. by 5 wickets or by 2 runs) |
| `outcome` | VARCHAR(50) | Was a winner decided or no (win, draw, tie, etc.) |
| `potm` | VARCHAR(100) | Player of the Match |
| `team_type` | VARCHAR(20) | international/club |
| `team_1` | VARCHAR(100) | Team 1 |
| `team_2` | VARCHAR(100) | Team 2 |
| `toss_winner` | VARCHAR(100) | Toss winner |
| `toss_decision` | VARCHAR(10) | bat/field |
| `venue` | VARCHAR(250) | Stadium name |
| `city` | VARCHAR(100) | City |

#### Table 2: deliveries (Ball-by-Ball)

| **Column Name** | **SQL Type** | **Desc.** |
| :--- | :--- | :--- |
| `match_id` | VARCHAR(50) | Foreign Key referencing `matches(match_id)` |
| `innings_no` | INT | Innings sequence (1, 2, 3, or 4) |
| `over_no` | INT | The over number (0, 1, 2...) |
| `ball_no` | INT | The ball number within the over (1, 2, 3...) |
| `batter` | VARCHAR(100) | Name or ID of the batter |
| `bowler` | VARCHAR(100) | Name or ID of the bowler |
| `non_striker` | VARCHAR(100) | Name or ID of the non-striker |
| `runs_batter` | INT | Runs scored off the bat |
| `runs_extras` | INT | Extra runs awarded (wides, noballs, legbyes, etc.) |
| `extra_type` | VARCHAR(20) | Nullable (wides, noballs, byes, legbyes, penalty) |
| `wicket_fell` | BOOLEAN | True/False |
| `player_out` | VARCHAR(100) | Nullable (Name of the player dismissed) |
| `dismissal_kind` | VARCHAR(50) | Nullable (caught, bowled, run out, lbw, etc.) |
| `fielder` | VARCHAR(50) | Nullable Name of fielder that completed the catch or run out |

#### Table 3: players

| **Column Name** | **SQL Type** | **Desc.** |
| :--- | :--- | :--- |
| `player_id` | VARCHAR(50) | Primary Key (corresponds to the unique registry ID in the JSON) |
| `player_name` | VARCHAR(150) | The full name of the player |

#### Table 4: match_to_players 

| **Column Name** | **SQL Type** | **Desc.** |
| :--- | :--- | :--- |
| `match_id` | VARCHAR(50) | Composite Primary Key / Foreign Key referencing `matches(match_id)` |
| `player_id` | VARCHAR(50) | Composite Primary Key / Foreign Key referencing `players(player_id)` |
| `team_name` | VARCHAR(100) | The team the player played for in this specific match |

Then I wrote a script that extracts this data in the format I want it.

For now I have 4 lists with all the data, I will work transferring this data into SQL next.

## 06/05/26

Today was focused entirely on sifting through the Cricsheet JSON files and finalizing the data pipeline to SQL. I had to pivot my approach midway through, but I successfully got all the data exported.

Here is a breakdown of how today went and my findings:

Today, I first learned how to handle virtual downloads, allowing the script to pull the zip archives directly from Cricsheet into memory instead of saving them to my local drive. This was done via the zipfile library.

I originally built the parsing logic using Pandas DataFrames for each table. While it functioned correctly, the processing time was way too high. I scrapped the DataFrames and rewrote the logic using native Python lists of dictionaries, which drastically improved the execution speed. I learned in class about the efficiency of hash maps and this project displays that efficiency perfectly!

Last, I mapped out the necessary JSON data and used the psycopg2 library to batch-insert those dictionary lists directly into the local database.

This was my first time working with PostgreSQL and psycopg2. Figuring out how to bridge the gap between a Python script and a live database was a valuable learning experience. Next I need to figure out how to update my db automatically (every week or month or so.)

I ended up with **11 million** (11,207,265) deliveries of data in the end! 

Code Attachment: View code [here](/exportDataToSQL.py)

*log to be continued...*
