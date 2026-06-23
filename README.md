*This project has been created as part of the 42 curriculum by dbozic, itykhono, jzackiew, mamichal, mbudkevi.*

# 42_ft_transcendence

## 🟥Description🟥 ```overview & clear name```
**QUIZSENDENCE** is a **Game Show Webapp** that lets you and your friends take part in a gameshow based on Fifteen to One.

### Key features ```key features```
- **Online Multiplayer** Game Show based Quiz.
- **Friends system**.
- **Text chats** between Friends and open text chat in-game.
- **Player Statistics**.
- **Player Profiles**.
- **LLM** based question generator for lobbies.
- **Mobile Support** along with **multi-browser support**.
- **Admin Panel** with database and user control.

### How to win?
The game show has you gain points by answering questions correctly. You must avoid answering incorrectly as you lose one of your three lives for each question you get wrong!

Unlike other game shows where contestants rush to answer first, players nominate each other in a system of "hand down the hot seat" to try eliminate the other players.

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
- **Tech Lead** - **mamichal** - Responsible for the choice of technological stack, researched different architectural decisions and proposed solutions based on data and our unique use case.
- **Developer** - **mbudkevi** - Responsible for implementing assigned features, writing tests, reviewing teammates' pull requests and documenting changes.
- **Developer** - **itykhono** - <Fill_In> <ITYKHONO>
### 🟪 Project management
#### Team organisation ```task distribution, meetings, project management, communication channels, and tools used for project management.```
**Meetings** - We held many meetings throughout our time working together. We first held organisational meetings, followed by meetings to find the project idea we would work on as well as our Project Owner. When work started on the project we began with our **weekly meetings** later transitioning into **bi-weekly meetings**, then **daily meetings** once we entered our crunch.

**Project Management** & **Task distribution** - Utilising **Github Projects** jzackiew set up the initial issues list to conform with his business requirements. The whole team **would take the highest priority issues and work on them** on seperate branches. Once an issue was finished we would have other members of the team review it and give feedback before it was either rejected or merged with main.

**In general we split our work into areas**. **dbozic** focused on AI and auxillery tasks, **itykhono** focused on frontend, **jzackiew** focused on game logic, **mamichal** focused on devops and **mbudkevi** focused on backend. This was a general guideline for who would take what.

**Communication Channels** - We used **Slack** for messaging, **Google Meet** for anyone who couldn't make it to our meetings in person, and **Github projects** to communicate large issues and code reviews. **A lot of our communcation came from sitting together on campus**.

### 🟦 Technical Stack ```frontend stack & framework, backend stack & framework, database system and why it was chosen, any other significant technologies or libraries, justification for major techncal choices```
- **Frontend technologies and frameworks**
  - **React**
  - **CSS Modules**
  - <Fill_in_or_delete> <ITYKHONO>
- **Backend technologies and frameworks**
  - **Django Rest Framework**
  - **Django Channels**
  - <Fill_in_or_delete> <JZACKIEW>
- **DevOps**
  - **Docker**
  - **NGINX**
  - **GitHub Workflows**
- **Database system and why it was chosen**
  - **PostgreSQL** - mature, free, first-class support in Django and it handles concurrent writes to game state safely.
- **Any other significant technologies or libraries**
  - **Pydantic** - Data Validation.
  - **Google Gemini API** - LLM calls.
  - **Redis** - Caching.
  - **Playwright** - End to End testing across multiple browsers
- **Justification for major techinical choices** - **Django Rest Framework** was chosen for its **ORM**, **Serializers** and **Authentication and permission system** along with other out of the box tools. **Redis** was used as a forward looking improvement over Djangos caching and channel tools. **React** was chosen for <ITYKHONO>

### 🟩 Database Schema ```visual representation or description of the database structure, tables/collections and thier relationships, Key fields and data types.```
**Our database structure can be found in image form at:** <directory_to_database_structure_image> <JZACKIEW>

**Our tables and collections and their relationships:** 
On the identity and social side, the entry point is the `User` model. Each user has at most one `UserProfile` (one-to-one, kept separate so we can add profile fields later without touching the auth table). Each user can have `SocialAccount` row, which link a Django user to an external OAuth identity such as Google. 
Friendships are stored in `Friendship`, which has two foreign keys back to `User` (`user` and `friend`); we write both directions when a request is accepted so the friendship is bidirectional in practice. Pending invites live in `FriendRequest`, also with two foreign keys back to `User` (`from_user` and `to_user`); rows are deleted once the request is accepted or declined.
<Fill_In>  <JZACKIEW>

**Key fields and data types:** 
- **User** — `id` (BigInt PK), `username` (unique varchar), `email` (unique email), `password` (hashed varchar), `is_active` (bool), `date_joined` (timestamp). Extends Django's `AbstractUser`; only the fields the application actually reads or writes are listed here.
- **UserProfile** — `id` (BigInt PK), `user` (one-to-one FK to `User`), `avatar` (image, nullable).
- **SocialAccount** — `id` (BigInt PK), `user` (FK to `User`), `provider` (varchar, e.g. `google`), `uid` (varchar - provider's stable user id), `created_at` (timestamp). Unique together on `(provider, uid)` so the same Google account cannot be linked twice.
- **Friendship** — `id` (BigInt PK), `user` (FK to `User`), `friend` (FK to `User`), `created_at` (timestamp). Unique together on `(user, friend)`.
- **FriendRequest** — `id` (BigInt PK), `from_user` (FK to `User`), `to_user` (FK to `User`), `created_at` (timestamp). Unique together on `(from_user, to_user)`.
<Fill_In> <JZACKIEW>

### 🟨 Features List ```complete list of features, who worked on what feature, brief description of each feature```
- **Online Multiplayer** Quiz Game Show.
- **Account Management**.
- **Friends system**.
- **Text chats** between Friends and open text chat in-game.
- **Player Statistics**.
- **LLM** based question generator for lobbies.

**Complete list of implemented features:**

**Online Multiplayer Game Show based Quiz** - An online game which players can host then compete in by nominating players to answer game show questions.
<br> **Game Design**, **Fullstack Implementaton**, and **graceful disconnections** by: **jzackiew**.
<br> **Game instructions** by: **mbudkevi.**

**Accounts and Account Management** - User account creation and profiles which display a players information along with user online presence.
<br> **Authentication** by: **mamichal and mbudkevi**.
<br> **Google OAuth and is online status** by: **mbudkevi**.
<br> **Frontend implementation** by: **itykhono**.

**Friends System** - A system where players can search for other players by username. They can add or remove friends to open a direct text chat.
<br> **Backend logic design and database relationship model** by: **mbudkevi**.
<br> **Frontend implementation** by: **itykhono**.

**Text Chats** - A websocket based system that allows users to directly communicate to each other by text live. You can text chat in public lobbies as well as directly with friends.
<br> **Websocket Architecture**, and **History Pagenation** by: **jzackiew**.
<br> **Backend Chat Logic**, and **Authentication** by: **mbudkevi**.
<br> **Frontend implementation** by: **itkyhono**

**Player Statistics** - A place on the home page where users can check their game statistics.
<br> **Statistic Tracking** by: **jzackiew**.
<br> **Frontend integration** by: **itykhono**.

**LLM based question generator for lobbies** - A button that allows the host of a lobby to add more questions to his quiz using AI. The AI generates similar questions to those already present in the lobby. The generated questions are added to the database for admin review and integration into the games questionbase.
<br> **LLM Integration**, **Game Session Integration**, **Database Persistence**, **Rate limitation**, and **Duplicate Protection** by: **dbozic**.
<br> **Frontend integration** by: **jzackiew**.

### 🟧 Modules ```List all chosen modules, point calculation, justification for each choice, how each module was implented, which team members did what```
### Complete list of chosen modules:

## 🌐 Web

### Minor - Use a frontend framework

 **React** was our choice of frontend framework as it <ITYKHONO> 

### Minor - Use a backend framework

- **People Involved: Everyone**
- We used **Django** as our backend framework.
- **Why this module?** - **Django** was chosen for its great out of the box capabilities like the **Django ORM** which allowed us to get an additional minor module. It allowed us to easily use **Redis** for caching and channels (WebSockets) with ease.

### Major - Implement real-time features using WebSockets or similar technology.

- **People Involved: jzackiew, itykhono** 
- <How_the_module_was_implemented>. <JZACKIEW>
- **Why this module?** - <Why_this_module_was_chosen>. <JZACKIEW>

### Major - Allow users to interact with other users.

- **People Involved: jzackiew, mbudekevi, mamichal, itykhono** 
- We have a /home/ page where once logged in a user can look for users, view their profiles, add or remove them as friends and message with them live. During live games players can chat with each other using a public text chat.
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
- Manually tested the app across different browsers both `Chromium (Blink + V8)` and `Firefox (Gecko + SpiderMonkey)` based. Implemented End to End tests with `playwright` to automate functional testing of the webapp's features and ensuring their proper behaviour.
- **Why this module?** - We wanted to make the app works flawlessly across different browsers and devices.

## 👥 User Management

### Major - Standard user management and authentication.

- **People Involved: mbudkevi, mamichal**
- Custom `User` model extending Django's `AbstractUser` with a unique email. It consist of registration, login and logout endpoints. Login accepts either email or username. Avatar uploads through a separate `UserProfile` model. Online status is tracked in-memory by counting each user's open WebSocket connections, then broadcast over the same Channels layer the chat uses.
- **Why this module?** - Since the project is a multiplayer game, having accounts and profiles was the natural starting point. Without them there is no way to identify players between sessions and build a friends list.

### Minor - Implement remote authentication with OAuth 2.0

- **People Involved: mbudkevi**
- A `SocialAccount` model links a Django user to a Google identity. The login endpoint builds Google's authorization URL; the callback exchanges the code for a token, fetches the user's email and profile and either logs in the existing user or creates a new one and links it.
- **Why this module?** - Most users prefer one-click sign in and registration, so it adds convenience for users.

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

- **What technical challenges it addresses** - The largest technical challenge with this module was **response validation**. LLMs are infamously bad at following exact rules. **Pydantic** was used for guaranteeing a safe answer format, and the content of the response was fine tuned through human readable instructions. Other challenges included **rate limiting**, and **integration** of answers into live lobbies and the persistent database.

- **How it adds value to your project** - Adding new, on theme but different, questions into each game prevents long time users from learning a majority of questions and their answers by heart. Generating questions adds excitement while also expanding the core question base that the quiz game relies on.  

- **Why it deserves Major module status (2 points).** - This module greatly resembles the module **"Major Module: Implement a complete LLM system interface"**. Below is a list of the requirements of the original module next to the counter part.
  + **Original:** Generate text and/or images based on user input.<br> **Counterpart:** Generate Questions with their answers and catagories based on the current lobbies question pool.
  + **Original:** Handle streaming responses properly. <br> **Counterpart:** Handle updating a game sessions question base as well as implementing persistence for future use of the generated questions.
  + **Original:** Implement error handling and rate limiting. <br>**Counterpart:** Implement error handling and rate limiting.

## Devops

### Minor Module of Choice - Continuous Integration

- **People Involved: mamichal, jzackiew**
- Implement a Continuous Integration for the project providing instant developer
  feedback after running the provided test suite using GitHub Workflows.
- **Why this module?** - We chose this module because it helped us speed
up the development process. It allowed us to know when a pull request broke a functionality
and therefore fix it before any code review would be conducted. It also ensured
that all automated tests pass after merging to main branch.

- **What technical challenges it addresses** - It solves the problem of
automated testing to make sure that all the tests pass properly before
conducting a code review and verified that a merge conflict did not break any
of the functionalities and helped us save on development time.

- **How it adds value to your project** - It helps us make sure that everything
works as expected and ensures that we do not introduce bugs,
especially when merging a pull request to the main branch.  

- **Why it deserves Minor module status (1 points).** It is not as extensive as
a full CI/CD pipeline which would definitely be a Major module, however it does
bring significant value in terms of safety, efficiency, and it provides instant
feedback to the whole development team through the GitHub UI.

**Total Points = 22**

### ⬜️ Individual Contributions ```Detailed breakdown of what each team member contributed, specific features, modules, or components implemented by each person. any challenges faced and how they were overcome.```

### dbozic - Scrum Master
#### Contributions
- Implemented the AI-powered Question Expander.
- Lead researcher for potential AI modules and AI integration.
- Assisted in Code review and organised live game tests.
- Refined the questions data set for use in the final product.
- Organised meetings and removed blockers.
- Wrote the README.md.
#### Specific features, modules, or components
- AI Question Expander major module.
- LLM integration.
- User rate limiting for AI requests.
- Database persistence and updating live lobbies.
- Documentation.

#### Challenges faced
- My largest technical challenge was developing and integrating the question expander. It required me to learn new tools like Python, an authenticated API, a web developement framework, an ORM, REST, rate limiting specific users, using external tools for format validation along with many other things that were cut from the final version.
<br> Looking back I am amazed I was able to start work on such a module as my first issue.
- A small but unusual challenge I faced was reforming the base list of questions and answers originating from a Polish gameshow. I found a method to automatically filter out questions which only people familiar with Polish culture would know along with translating and sorting the rest.

### itykhono - Developer <ITYKHONO>
- Frontend
-

### jzackiew - Product Owner <JZACKIEW>
- 
-

### mamichal - Tech Lead

#### Contributions

- DevOps and backend developer, focused mainly on setup of the environment and
ensuing proper deployment across multiple systems. Also contributed to some
frontend tasks.

#### Specific features, modules, or components

- DevOps - setting up a contenerized environment with proper communication and
volume persistence for both production environment and development playground
- Automated deployment via Makefile
- Added other useful automations for development purposes
- Contributed to CI setup
- Configured NGINX as a reverse proxy for HTTPS and WSS connections
- Setup Redis as an in memory database
- Blocked direct client-side access to /api/
- Ensured proper cross-browser support and implemented E2E testing
- Ensured proper distribution of CSRF
- Prepared database populating script for evaluation and testing purposes
- Implemented frontend routing guards
- Prepared legal sites

#### Challenges faced

### mbudkevi - Developer <MBUDKEVI>
- Backend developer covering authentication, the friends system, real-time presence, the chat backend and the project's initial database setup.
- Reviewed teammates' pull requests and helped resolve a number of migration conflicts during merges.

#### Specific features, modules, or components
- Custom `User` model and `UserProfile`, initial data base setup.
- Registration / login / logout endpoints.
- Email-or-username login backend (case-insensitive matching, `@` disallowed in usernames).
- WebSocket authentication on both the game and chat consumers (anonymous connections are rejected at handshake).
- Friends system: `Friendship` and `FriendRequest` models, accept / decline / list endpoints.
- Real-time online-presence registry: tracks each user's open WebSocket connections and broadcasts online/offline transitions over the same Channels layer the chat uses.
- Google OAuth 2.0 backend end-to-end: `SocialAccount` model, login and callback endpoints, the PKCE-based authorization flow (`code_verifier` / `code_challenge` / `state`), and id-token verification.
- Chat backend: consumers and the rule that only friends can DM each other.

#### Challenges faced
Google OAuth was the trickiest piece for me. I had not worked with the protocol before and there were a lot of small moving parts (state cookie, PKCE verifier, id-token verification) that all had to fit together before anything worked end to end.
