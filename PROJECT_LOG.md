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

### Transfer data from Cricsheet to PostgreSQL
* First I wanted to visualize the cricsheet data and understand its format.
  * The data is stored in JSON, where each JSON file represents one match.
* Next, I need to figure out the missing data. Some important pieces of data are exempt from the dataset, I need to identify this and use other sources to fill it in. 

*(Entry to be continued)*
