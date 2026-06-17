*This project has been created as part of the 42 curriculum by dbozic, itykhono, jzackiew, mamichal, mbudkevi.*

# 42_ft_transcendence

## 🟥Description🟥 ```overview & clear name```
**QUIZSENDENCE** is a **Game Show Webapp** that lets you and your friends take part in a gameshow based off <Game_Show_Name>.

### Key features ```key features```
- Login - <Fill_In>
- <Fill_In>

### How to win?
The game show has you gain points by answering questions correctly. You must avoid answering incorrectly as you lose one of your three lives for each question you get wrong!

Unlike other game shows where contestants rush to answer first, players nominate each other in a system of "hand down the hot seat" to try elimitate the other players.

The winner is chosen when all the questions are answered, or if all but one player have fallen.

**Do you have what it takes to win?**

### Make a profile, add friends and chat!
We provide a player profile along with friends system to allow players to chat between games!

Found a worthy opponent and want a rematch? **Add them and send them a room key!**

Had enough of losing to them? **Unfriend them and see them disappear!**

### How to play?
Want to host a game? **Simply go to <Final_URL>, Register or Log in, Create a lobby, and send your friends the lobby ID.**

Having trouble joining a friend who is already hosting lobby? **Go to <Final_URL>, Register or Log in then press JOIN ROOM and ask your friend for the room code.**

### Why quizsendence? ```goal```
Our goal was to recreate the game show Fifteen to One in webapp form. Each persons personal goals varied but all of us had the common goal of passing ft_transcendence.

## 🟪Instructions🟪
### How to host the website ```compilation, installation, and/or execution```
- Make sure you meet all the prequisites listed in the **Prerequisites** section.
- Download the repository using: ```git clone <repository_id>```
- Locate the .env.example file. Copy it and rename the copy to .env.
- (**IMPORTANT**) Open the newly made .env file and change all necessary fields. *For limited testing you don't have to change anything.*
- Update all README.md <Final_URL> variables to match your configured .env.
- Enter the project folder and run: ```make up```
- Check whether the server is running by visiting <Final_URL>.

### Are you already hosting the website and want to play?
**Look in the section above for HOW TO PLAY?** 

### Prerequisites ```software, tools, versions, configuration like .env setup, etc.```
**The basics in order to run the installation** Versions aren't strict but if you encounter errors change to the newest versions available in Q1 2026.
- **A Linux environment**
- **Git** for downloading the project files.
- **make** for the Makefile.
- **docker** && **docker compose** for containerisation.
- **python3** && **python3 virtual environment**.
- **pip** && **npm** for additional package installion.

**For fast installation from zero**
```
sudo apt install \
make \
docker.io \
docker-compose-v2 \
python3 \
python3-venv \
python3-pip \
npm
```

**The setup process is automated by the Makefile and Docker.** They deal with the rest of the requirements.

**If you wish to do things manually you will need to:**
- create a virtual environment with ```python3 -m venv .venv```
- activate the virtual environment with ```source .venv/bin/activate``` 
- install all additional prerequisite packages with ```pip install -r server/requirements.txt```

You might want to do this if automatic migration is not working.

## 🟦Resources🟦 

### General References
#### ```section listing classic references related to the topic (documentation, articles, tutorials, etc.)```
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Service layer pattern](https://github.com/HackSoftware/Django-Styleguide)
- [Websockets docs and tutorial](https://channels.readthedocs.io/)
- <Fill_In>

### Individual Resources and AI usage
#### ```section listing classic references related to the topic (documentation, articles, tutorials, etc.), as well as a description of how AI was used specifying for which tasks and which parts of the project.```
This will be separated into a section for each person as each person worked on separate tasks and may have used different documentation.
### dbozic
#### What references did you use and for what topic?
+ **AI integration**
  - During my SPIKE on integrating LLM - <Fill_In>
  - other stuff - <Fill_In>
  - django - <Fill_In>
  - redis - <Fill_In>
  - <Fill_In>
  - <Fill_In>
+ **Persistence and working with Django**
  - django framework documentation - <Fill_In>
  - <Fill_In>
#### How did you utilize AI during this project?
When I started work on the project I used Github Copilot to summarise what had already been made and how I should go about integrating my then standalone LLM based question generation program into my first glimpse of the Django framework.

I used a conversational assistant to help me learn about possible solutions when assigned to a SPIKE where I explored various ways I could use RAG *(Retrieval-Augmented Generation)* in our project as well as alternate ways we could solve answer verification later on.

I also explored using Github Copilot to assist me with writing code. I was pleasantly surprised by how efficient it was to integrate into daily coding routine. I unfortunately ran out of tokens after about a week of this and was forced to go back to manually writing code.

### itykhono
#### What references did you use and for what topic?
#### How did you utilize AI during this project?

### jzackiew
#### What references did you use and for what topic?
#### How did you utilize AI during this project?

### mamichal
#### What references did you use and for what topic?
#### How did you utilize AI during this project?

### mbudkevi
#### What references did you use and for what topic?
#### How did you utilize AI during this project?

## 🟩Additional sections🟩

### 🟥 Team Information 
**We separated our work into roles defined within the subject** ```Assigned roles, Brief description of their responsibilities```
- **Project Owner** - **jzackiew** - Responsible for the vision of the project, set priorities for features and ensured the project met the subjects and team goals.
- **Scrum Master** - **dbozic** - Responsible for organising the team and their productivity. Facilitated team Brain Storming and held meetings to settle on a project plan. Scheduled common Scrum meetings to keep everyone up to date and clear blockers.
- **Tech Lead** - **mamichal** - <Fill_In>
- **Developer** - **mbudkevi** - <Fill_In>
- **Developer** - **itykhono** - <Fill_In>
### 🟪 Project management
#### Team organisation ```task distribution, meetings, project management, communication channels, and tools used for project management.```
**Meetings** - We held many meetings throughout our time working together. We first held organisational meetings, followed by meetings to find the project idea we would work on as well as our Project Owner. When work started on the project we began with our **weekly meetings** later transitioning into **bi-weekly meetings**, then **daily meetings** once we entered our crunch.

**Project Management** & **Task distribution** - Utilising **Github Projects** jzackiew set up the initial issues list to conform with his business requirements. The whole team **would take the highest priority issues and work on them** on seperate branches. Once an issue was finished we would have other members of the team review it and give feedback before it was either rejected or merged with main.

**In general we split our work into areas**. **dbozic** focused on AI and auxillery tasks, **itykhono** focused on frontend, **jzackiew** focused on game logic, **mamichal** focused on devops and **mbudkevi** focused on backend. This was a general guideline for who would take what.

**Communication Channels** - We used **Slack** for messaging, **Google Meet** for anyone who couldn't make it to our meetings in person, and **Github projects** to communicate large issues and code reviews. **A lot of our communcation came from sitting together on campus**.

### 🟦 Technical Stack ```frontend stack & framework, backend stack & framework, database system and why it was chosen, any other significant technologies or libraries, justification for major techncal choices```
- **Frontend technologies and frameworks** - <Fill_In>
- **Backend techonlogies and frameworks** - <Fill_In>
- **Database system and why it was chosen** - <Fill_In>
- **Any other significant technologies or libraries** - <Fill_In>
- **Justification for major techinical choices** - <Fill_In>

### 🟩 Database Schema ```visual representation or description of the database structure, tables/collections and thier relationships, Key fields and data types.```
**Our database structure can be found in image form at:** ```<Insert_DIR_to_database_structure_image> ```

**Our tables and collections and their relationships:** <Fill_In>

**Key fields and data types:** <Fill_In>

### 🟨 Features List ```complete list of features, who worked on what feature, brief description of each feature```

**Complete list of implemented features:**
**<Feature>** - <Description> - **Made by:** <Person(s)>.

**<Feature>** - <Description> - **Made by:** <Person(s)>.

**<Feature>** - <Description> - **Made by:** <Person(s)>.

**<Feature>** - <Description> - **Made by:** <Person(s)>.

### 🟧 Modules ```List all chosen modules, point calculation, justification for each choice, how each module was implented, which team members did what```
**Complete list of chosen modules:**
**<Module>** - **<Minor/Major>** - **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

**<Module>** - **<Minor/Major>** - **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

**<Module>** - **<Minor/Major>** - **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

**<Module>** - **<Minor/Major>** - **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

**Total Points = <total_count>**

### ⬜️ Individual Contributions ```Detailed breakdown of what each team member contributed, specific features, modules, or components implemented by each person. any challenges faced and how they were overcome.```
