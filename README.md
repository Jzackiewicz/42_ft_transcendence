*This project has been created as part of the 42 curriculum by dbozic, itykhono, jzackiew, mamichal, mbudkevi.*

# 42_ft_transcendence

## 🟥Description🟥 ```overview & clear name```
**QUIZSENDENCE** is a **Game Show Webapp** that lets you and your friends take part in a gameshow based off Fifteen to One.

### Key features ```key features```
- **Online Multiplayer** Quiz Game Show.
- **Friends system**.
- **Text chats** between Friends and open text chat in-game.
- <NOT_YET_IMPLEMENTED **Player Statistics**>.
- <NOT_YET_IMPLEMENTED **Player Profiles**>.
- **LLM** based question generator for lobbies.
- **Mobile Support** along with **multi-browser support**.
- **Admin Panel** with database and user control.

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

### General References ```section listing classic references related to the topic (documentation, articles, tutorials, etc.)```

- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Django ORM](https://docs.djangoproject.com/en/6.0/topics/db/models/)
- [Django Authentication](https://docs.djangoproject.com/en/6.0/topics/auth/)
- [Django Migrations](https://docs.djangoproject.com/en/6.0/topics/migrations/)
- [Redis](https://channels.readthedocs.io/en/stable/topics/channel_layers.html)
- [Service layer pattern](https://github.com/HackSoftware/Django-Styleguide)
- [Websockets docs and tutorial](https://channels.readthedocs.io/)
- [Gemini integration](https://ai.google.dev/gemini-api/docs)
- [React docs](https://pl.react.dev/)
### AI Usage ```a description of how AI was used specifying for which tasks and which parts of the project.```

**We used a wide range of AI assistence when it came to work and research. Below is listed all the uses of AI our team utilised:**
- **Research** on how to use new techologies.
- Assistance with **design choice research**.
- **Code summarisation** for individual understanding foreign sections of the codebase.
- **Writing tedious and repetitive code that was already understood.**
- **Debugging** tasks and **error summarisation**.

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
- **Backend technologies and frameworks** - <Fill_In>
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
### Complete list of chosen modules:

## 🌐 Web

### Major - Use a framework for both the frontend and backend

- **People Involved: Everyone**
- We used **Django** as our backend framework and **React** as our frontend framework.
- **Why this module?** - **Django** was chosen for its great out of the box capabilities like the **Django ORM** which allowed us to get an additional minor module. It allowed us to use **Redis** for caching and channels (WebSockets) with ease. <Add_onto_this_if_you_want>

### Major - Implement real-time features using WebSockets or similar technology.

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

### Major - Allow users to interact with other users.

- **People Involved: <People_Involved>**
- We have a /home/ page where once logged in a user can look for users, <NOT_YET_IMPLEMENTED view their profiles>, add or remove friends and message with them live. <NOT_YET_IMPLEMENTED During live games players can chat with each other using a lobby sized live chat.>
- **Why this module?** - This module fit very well considering the aspect of the game. The idea of players interacting mid match then adding each other after the match to discuss the game or organise another one is a logical one.

### Minor - Use an ORM for the database.

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

## 💠 Accessibility and Internationalization

### Minor - Support for additional browsers.

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

## 👥 User Management

### Major - Standard user management and authentication.

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

### Minor - Implement remote authentication with OAuth 2.0

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

## 🔮 Gaming and user experience

### Major - Implement a complete web-based game where users can play against each other.

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

### Major - Remote players — Enable two players on separate computers to play the same game in real-time

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

### Major - Multiplayer game (more than two players)

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

### Minor - Implement spectator mode for games.

- **People Involved: <People_Involved>**
- <How_the_module_was_implemented>.
- **Why this module?** - <Why_this_module_was_chosen>.

## 🔮 Artificial Intelligence

### Major Module of Choice - <Question_Expander>.

- **People Involved: dbozic, jzackiew**
- <How_the_module_was_implemented>.
- **Why this module?** - We chose this module as it is a core concept of our game; AI generated questions. It also opened up the possibility of implementing RAG (Retrieval Based Generation) which could have been an additional Major Module.

- **What technical challenges it addresses** - <Fill_in>

- **How it adds value to your project** - <Fill_in>

- **Why it deserves Major module status (2 points).** - This module greatly resembles the module **"Major Module: Implement a complete LLM system interface"**. Below is a list of the requirements of the original module next to the counter part.
  + **Original:** Generate text and/or images based on user input.<br> **Counterpart:** Generate Questions with their answers and catagories based on the current lobbies question pool.
  + **Original:** Handle streaming responces properly. <br> **Counterpart:** Handle updating a game sessions question base as well as implementing persistence for future use of the generated questions.
  + **Original:** Implement error handling and rate limiting. <br>**Counterpart:** Implement error handling and rate limiting.

**Total Points = <total_count>**

### ⬜️ Individual Contributions ```Detailed breakdown of what each team member contributed, specific features, modules, or components implemented by each person. any challenges faced and how they were overcome.```

#### dbozic
**AI and RAG SPIKE**

**The AI based Question Expander**

**Peer Review**

**The README.md**

#### itykhono

#### jzackiew

#### mamichal

#### mbudkevi
