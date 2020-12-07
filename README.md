# COD-Scoreboard-Parser
Like many COD fans, we started to play a lot of the new gunfight mode on Modern Warfare. Unfortunately, the online multiplayer just supports 2v2 or 3v3 teams... so we started playing private matches with several of our friends. 
One day, one of our friends thought it would be cool if we could collect our stats cumulatively. So that brings us to this project...

Flow:
- Take screenshot on xbox of scoreboard
- Upload to Gmail
- Run cronjob daily to:
    - Download attachments from unread mail on dedicated gmail account for gunfight screenshots
    - Parse photos for stats
    - Upload stats to online database
- Have our friends go online to look up their stats

Eventually we believe we can add some machine learning algorithms on the data to see if we can predict who would win with specific combos of teams on certain stages.

# Setup PC
You have two options, run locally or run with docker

## Local Setup
If you want to just use your host to run everything, first do a pip install on all the libraries in the requirements.txt file.

## Docker Setup

If using OSX, you need to install XQuartz so you can use the Python GUI with Docker

[How to Use x11 and Docker](https://medium.com/@mreichelt/how-to-show-x11-windows-within-docker-on-mac-50759f4b65cb)

## GMAIL Setup

There is a feature to download all the unread email attachments (in our example, we have an email dedicated to screenshots from Xbox). Before you run this feature....

1) First go here: [Gmail Python QuickStart](https://developers.google.com/gmail/api/quickstart/python) and run Step 1 to get the credentials.json file and put it at the top level of the repo.
2) Comment out "COPY token.pickle ." in the Dockerfile
3) Build the docker container
4) Run the docker container: "./run DL"
5) Take the link from the console and paste it in a browser and follow the steps to give permissions to modify your gmail messages.
6) Copy the key from the browser into the console
7) Copy the token.pickle file from $HOME on your host to the top level of the repo
8) Uncomment the "COPY token.pickle ." file in the Dockerfile
9) Rebuild the container

*** It is not recommended to push any key file to a public git repo... to be safe, these files were added to .gitignore to prevent an accidental commit.

## Building with Docker
...
docker build -t cod .
...

## Running Docker
This script will run the GUI version of the container.
...
./run GUI
...

If you want to just run the parser without the GUI do... the paths are relative to the $HOME path on your PC
...
./run /pathtoinputs_incontainer /pathtooutputs_incontainer
...

if you want to just download the latest unread messages from gmail
...
./run DL <UNREAD/ALL> /pathtoinputs_incontainer
...


- [ ] Adjust to handle after match score screen
  - Incase the 'SCOREBOARD' screen is not capture process and alternative
- [ ] Automatically find data locations
  - Should resolve many image difference issues
- [ ] Improve recognition by running more tests
  - A very clear '7' is not being recognized
- [ ] Handle differnt resolutions
  - Screen shots dont appear to be the same resolution when captured
- [ ] Handle the smaller scoreboard
- [ ] Save data to an online database
- [ ] Create front end webpage for others to come and view stats
- [ ] Integrate with machine learning to predict what team should win
