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


- [ ] Adjust to handle after match score screen
  - Incase the 'SCOREBOARD' screen is not capture process and alternative
- [ ] Automatically find data locations
  - Should resolve many image difference issues
- [ ] Improve recognition by running more tests
  - A very clear '7' is not being recognized
- [ ] Handle differnt resolutions
  - Screen shots dont appear to be the same resolution when captured
