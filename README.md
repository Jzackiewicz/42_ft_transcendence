*This project has been created as part of the 42 curriculum by dbozic, itykhono, jzackiew, mamichal, mbudkevi.*

# 42_ft_transcendence

## 🟥Description🟥 ```overview & clear name```
**QUIZSENDENCE** is a **Game Show Webapp** that lets you and your friends take part in a gameshow based on Fifteen to One.

### Key features ```key features```
- **Online Multiplayer** Game Show based Quiz.
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
- [Documentation for custom-made styling minor module](https://github.com/Jzackiewicz/42_ft_transcendence/pull/165)
- <Fill_in_or_delete> <ITYKHONO>
- <Fill_in_or_delete> <JZACKIEW>
- <Fill_in_or_delete> <MAMICHAL>
- <Fill_in_or_delete> <MBUDKEVI>
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
- **Tech Lead** - **mamichal** - <Fill_In> <MAMICHAL>
- **Developer** - **mbudkevi** - <Fill_In> <MBUDKEVI>
- **Developer** - **itykhono** - <Fill_In> <ITYKHONO>
### 🟪 Project management
#### Team organisation ```task distribution, meetings, project management, communication channels, and tools used for project management.```
**Meetings** - We held many meetings throughout our time working together. We first held organisational meetings, followed by meetings to find the project idea we would work on as well as our Project Owner. When work started on the project we began with our **weekly meetings** later transitioning into **bi-weekly meetings**, then **daily meetings** once we entered our crunch.

**Project Management** & **Task distribution** - Utilising **Github Projects** jzackiew set up the initial issues list to conform with his business requirements. The whole team **would take the highest priority issues and work on them** on seperate branches. Once an issue was finished we would have other members of the team review it and give feedback before it was either rejected or merged with main.

**In general we split our work into areas**. **dbozic** focused on AI and auxillery tasks, **itykhono** focused on frontend, **jzackiew** focused on game logic, **mamichal** focused on devops and **mbudkevi** focused on backend. This was a general guideline for who would take what.

**Communication Channels** - We used **Slack** for messaging, **Google Meet** for anyone who couldn't make it to our meetings in person, and **Github projects** to communicate large issues and code reviews. **A lot of our communcation came from sitting together on campus**.

### 🟦 Technical Stack ```frontend stack & framework, backend stack & framework, database system and why it was chosen, any other significant technologies or libraries, justification for major techncal choices```
- **Frontend technologies and frameworks**
  - **React 19 with Typescript 6**
  - **CSS Modules**
  - <Fill_in_or_delete> <ITYKHONO>
  - <Fill_in_or_delete> <MBUDKEVI>
- **Backend technologies and frameworks**
  - **Django Rest Framework**
  - **Django Channels**
  - **Docker with Enginx**
  - <Fill_in_or_delete> <JZACKIEW>
  - <Fill_in_or_delete> <MAMICHAL>
- **Database system and why it was chosen**
  - **PostgreSQL** - Was selected due to it... - <MBUDKEVI>
- **Any other significant technologies or libraries**
  - **Pydantic** - Data Validation.
  - **Google Gemini API** - LLM calls.
  - **Redis - Caching**.
  - **<Maybe_Playwright>** - <MAMICHAL>
- **Justification for major techinical choices** - **Django Rest Framework** was chosen for its **ORM**, **Serializers** and **Authentication and permission system** along with other out of the box tools. **Redis** was used as a forward looking improvement over Djangos caching and channel tools. **React** was chosen for <ITYKHONO>

### 🟩 Database Schema ```visual representation or description of the database structure, tables/collections and thier relationships, Key fields and data types.```
**Our database structure can be found in image form at:** <directory_to_database_structure_image> <MBUDKEVI>

**Our tables and collections and their relationships:** <Fill_In> <MBUDKEVI>

**Key fields and data types:** <Fill_In> <MBUDKEVI>

### 🟨 Features List ```complete list of features, who worked on what feature, brief description of each feature```
- **Online Multiplayer** Quiz Game Show.
- **Account Management**.
- **Friends system**.
- **Text chats** between Friends and open text chat in-game.
- <NOT_YET_IMPLEMENTED **Player Statistics**>.
- **LLM** based question generator for lobbies.

**Complete list of implemented features:**

**Online Multiplayer Game Show based Quiz** - An online game which players can host then compete in by nominating players to answer game show questions.
<br> Game Design, Fullstack Implementaton, and **graceful disconnections** by **jzackiew**.
<br> Game instructions by **mbudkevi.**

**Accounts and Account Management** - User account creation and profiles which display a players information along with user online presence.
<br> **Authentication** by **mamichal and mbudkevi**.
<br> **Google OAuth and is online status** by **mbudkevi**.
<br> **Frontend implementation** by **itykhono**.

**Friends System** - A system where players can search for other players by username. They can add or remove friends to open a direct text chat.
<br> **Backend logic design and database relationship model** by **mbudkevi**.
<br> **Frontend implementation** by **itykhono**.

**Text Chats** - A websocket based system that allows users to directly communicate to each other by text live. You can text chat in public lobbies as well as directly with friends.
<br> **Websocket Architecture**, and **History Pagenation** by: **jzackiew**.
<br> **Backend Chat Logic**, and **Authentication** by **mbudkevi**.
<br> **Frontend implementation** by **itkyhono**

**Player Statistics** - A place on the home page where users can check their game statistics.
<br> **Statistic Tracking** by: **jzackiew**.
<br> **Frontend integration** by: **itykhono**.

**LLM based question generator for lobbies** - A button that allows the host of a lobby to add more questions to his quiz using AI. The AI generates similar questions to those already present in the lobby. The generated questions are added to the database for admin review and integration into the games questionbase.
<br> **LLM Integration**, **Game Session Integration**, **Database Persistence**, **Rate limitation**, and **Duplicate Protection** by **dbozic**.
<br> Frontend integration **jzackiew**.

### 🟧 Modules ```List all chosen modules, point calculation, justification for each choice, how each module was implented, which team members did what```
### Complete list of chosen modules:

## 🌐 Web

### Minor - Use a frontend framework

 **React** was our choice of frontend framework as it <ITYKHONO> 

### Minor - Use a backend framework

- **People Involved: Everyone**
- We used **Django** as our backend framework and **React** as our frontend framework.
- **Why this module?** - **Django** was chosen for its great out of the box capabilities like the **Django ORM** which allowed us to get an additional minor module. It allowed us to easily use **Redis** for caching and channels (WebSockets) with ease.

### Major - Implement real-time features using WebSockets or similar technology.

- **People Involved: jzackiew, itykhono** 
- <How_the_module_was_implemented>. <JZACKIEW>
- **Why this module?** - <Why_this_module_was_chosen>. <JZACKIEW>

### Major - Allow users to interact with other users.

- **People Involved: jzackiew, mbudekevi, mamichal, itykhono** 
- We have a /home/ page where once logged in a user can look for users, <NOT_YET_IMPLEMENTED view their profiles>, add or remove them as friends and message with them live. During live games players can chat with each other using a public text chat.
- **Why this module?** - This module fit very well considering the aspect of the game. The idea of players interacting mid match then adding each other after the match to discuss the game or organise another one is a logical one.

### Minor - Use an ORM for the database.

- **People Involved: Everyone**
- This module was implemented by default thanks to it coming with Django.
- **Why this module?** - ORMs simplify our work with the database, Django was selected partly because it came with one by default allowing us to work with our databases with ease, while gaining a free point. 

### Minor - Custom made design system with reusable components, including a proper color palette, typography, and icons.

- **People Involved: zjackiew, itykhono**
- <How_the_module_was_implemented>. <JZACKIEW>
- **Why this module?** - <Why_this_module_was_chosen>. <JZACKIEW>

## 💠 Accessibility and Internationalization

### Minor - Support for additional browsers.

- **People Involved: mamichal**
- <How_the_module_was_implemented>. <MAMICHAL>
- **Why this module?** - <Why_this_module_was_chosen>. <MAMICHAL>.

## 👥 User Management

### Major - Standard user management and authentication.

- **People Involved: mbudkevi**
- Is online status, <How_the_module_was_implemented>. <MBUDKEVI>
- **Why this module?** - <Why_this_module_was_chosen>. <MBUDKEVI>

### Minor - Implement remote authentication with OAuth 2.0

- **People Involved: mbudkevi**
- <How_the_module_was_implemented>. <MBUDKEVI>
- **Why this module?** - <Why_this_module_was_chosen>. <MBUDKEVI>

## 🔮 Gaming and user experience

### Major - Implement a complete web-based game where users can play against each other.

- **People Involved: jzackiew** 
- <How_the_module_was_implemented>. <JZACKIEW>
- **Why this module?** - <Why_this_module_was_chosen>. <JZACKIEW>

### Major - Remote players — Enable two players on separate computers to play the same game in real-time

- **People Involved: mamichal, jzackiew**
- <How_the_module_was_implemented>. <JZACKIEW>
- **Why this module?** - <Why_this_module_was_chosen>. <JZACKIEW>

### Major - Multiplayer game (more than two players)

- **People Involved: jzackiew**
- <How_the_module_was_implemented>. <JZACKIEW>
- **Why this module?** - <Why_this_module_was_chosen>. <JZACKIEW>

### Minor - Implement spectator mode for games.

- **People Involved: jzackiew**
- <How_the_module_was_implemented>. <JZACKIEW>
- **Why this module?** - <Why_this_module_was_chosen>. <JZACKIEW>

## 🔮 Artificial Intelligence

### Major Module of Choice - LLM Question Expander System.

- **People Involved: dbozic, jzackiew**
- It is shown as a host only button in the lobby screen. When pressed the lobby questions are sent to an LLM where additional similar questions are generated. Those questions are then added to the game session to be played, and saved persistently in the database for future use.
- **Why this module?** - We chose this module as it is a core concept of our game: AI generated questions. It also opened up the possibility of implementing RAG (Retrieval Based Generation) which could have been an additional Major Module.

- **What technical challenges it addresses** - The largest technical challenge with this module was **response validation**. LLMs are infamously bad at following exact rules. **Pydantic** was used for garuanteeing a safe answer format, and the content of the response was fine tuned through human readable instructions. Other challenges included **rate limitating**, and **integration** of answers into live lobbies and the persistent database.

- **How it adds value to your project** - Adding new, on theme but different, questions into each game prevents long time users from learning a majority of questions and their answers by heart. Generating questions adds excitement while also expanding the core question base that the quiz game relies on.  

- **Why it deserves Major module status (2 points).** - This module greatly resembles the module **"Major Module: Implement a complete LLM system interface"**. Below is a list of the requirements of the original module next to the counter part.
  + **Original:** Generate text and/or images based on user input.<br> **Counterpart:** Generate Questions with their answers and catagories based on the current lobbies question pool.
  + **Original:** Handle streaming responces properly. <br> **Counterpart:** Handle updating a game sessions question base as well as implementing persistence for future use of the generated questions.
  + **Original:** Implement error handling and rate limiting. <br>**Counterpart:** Implement error handling and rate limiting.

**Total Points = 21**

### ⬜️ Individual Contributions ```Detailed breakdown of what each team member contributed, specific features, modules, or components implemented by each person. any challenges faced and how they were overcome.```

### dbozic - Scrum Master
- Backend developer for the AI Question Expander.
- Lead researcher for AI modules and AI integration.
- Code reviewer and game tester.
- Question base refiner.
- Scrum master and organiser.
- Wrote the README.md.

### itykhono - Developer <ITYKHONO>
- Frontend
-

### jzackiew - Product Owner <JZACKIEW>
- 
-

### mamichal - Tech Lead <MAMICHAL>
- Devops
-

### mbudkevi - Developer <MBUDKEVI>
- Database
-
