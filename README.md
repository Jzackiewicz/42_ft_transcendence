*This project has been created as part of the 42 curriculum by dbozic, itykhono, jzackiew, mamichal, mbudkevi*

# 42_ft_transcendence

## 🟥Description🟥 ```overview```
**QUIZSENDENCE** is a **Game Show Webapp** that lets you and your friends take part in a gameshow based off <Game_Show_Name>.

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
- (**IMPORTANT**) Open the newly made .env file and change all necessary fields.
- Update all README.md <Final_URL> variables to match your configured .env.
- Enter the project folder and run: ```make up```
- Check whether the server is running by visiting your page.

### Are you already hosting the website and want to play?
**Look in the section above for HOW TO PLAY?** 

### Prerequisites
**The basics in order to run the installation**
- **A Linux environment**
- **Git** for downloading the project files.
- **make** for the Makefile.
- **docker** && **docker compose** for containerisation.
- **python3** && **python3 virtual environment** && **Node.js**.
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
nodejs \
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
- fee
- fi
- fo
- fum

### Individual Resources and AI usage ```section listing classic references related to the topic (documentation, articles, tutorials, etc.), as well as a description of how AI was used specifying for which tasks and which parts of the project.```
This will be separated into a section for each person as each person worked on separate tasks and may have used different documentation.
### dbozic
#### What references did you use and for what topic?
+ **AI integration**
  - rag
  - other stuff
  - django
  - redis
  - TEMP
  - TEMP
+ **Persistence and working with Django**
  - django framework documentation
  - etc.
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

### Team Information

### Project management

### Technical Stack

### Database Schema

### Features List

### Modules

### Individual Contributions

## 🟨

## 🟧