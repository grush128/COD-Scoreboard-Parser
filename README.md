# COD-Scoreboard-Parser

# Setup PC
You have two options, run locally or run with docker

## Local Setup
```
pip install numpy
pip install pytesseract
pip install opencv-python
```

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
./run DL /pathtooutputs_incontainer
...


- [ ] Adjust to handle after match score screen
  - Incase the 'SCOREBOARD' screen is not capture process and alternative
- [ ] Automatically find data locations
  - Should resolve many image difference issues
- [ ] Improve recognition by running more tests
  - A very clear '7' is not being recognized
- [ ] Handle differnt resolutions
  - Screen shots dont appear to be the same resolution when captured
