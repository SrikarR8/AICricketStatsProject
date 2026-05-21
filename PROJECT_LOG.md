# Project Log & Notes

## 5/11/26

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

## 5/13/26

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

## 5/20/26

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

## 5/21/26

### Creating the database

*(Entry to be continued)*
