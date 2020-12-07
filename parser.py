# Full image 2592 x 1458

# Scoreboard Text
# X:122 Y:67 W:412 H:61

# Top Team Name
# X:415 Y:610 W:319 H:61

# Top Score
# X:560 Y:670 W:192 H:103

# Bottom Team Name
# X:358 Y:1054 W:378 H:61

# Bottom Score
# X:554 Y:1110 W:190 H:103

# Map
# X:941 Y:355 W:491 H:40

# Match Time
# X:1779 Y:354 W:481 H:40

# Top R1
# X:832 Y:447 W:1414 H:38
# Top R1 Name
# X:832 Y:447 W:516 H:38
# Top R1 Stats
# X:1348 Y:447 W:897 H:38

# Top R2
# X:832 Y:485 W:1414 H:38

# Bottom R1
# X:832 Y:871 W:1414 H:38


import cv2
import numpy as np
import pytesseract
import math
import csv
import uuid
import base64
from difflib import get_close_matches
import sys
import os
import glob
import io
import PySimpleGUI as sg
import subprocess
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
from PIL import Image, ImageTk
from csv import reader

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def invert_colors(image):
    return cv2.bitwise_not(image)
    
def scale_image(image, height, width):
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow('resized image', resized)
    cv2.waitKey(0)
    return resized

def grab_data(image, X, Y, W, H, isNum, dataname=""):
    # --psm 6, 7
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_blacklist=&@'
    if isNum:
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:'

    crop_img = image[Y:Y+H, X:X+W]
    
    #if dataname.strip():
    #cv2.imshow(dataname, crop_img)
    #cv2.waitKey(0)
    print("Basic Crop: " + pytesseract.image_to_string(crop_img, config=custom_config))
    return pytesseract.image_to_string(crop_img, config=custom_config)


def make_int(str_num):
    return int(str_num.replace('o', '0').replace('a', '0').replace('O', '0').replace('l', '1').replace('L', '1').replace('i', '1').replace('I', '1').replace('.', ''))

def isWinner(mine, other):
    return str(make_int(mine.strip()) > make_int(other.strip()))
    
    
def match_user_name(name):
    if not os.path.exists('usernames.txt'):
        with open('usernames.txt', 'w'): pass
    with open('usernames.txt', 'r+') as f:
        lines = f.read().splitlines()
        lines = [line.strip() for line in lines]
        matches = get_close_matches(name, lines, n=1, cutoff=0.3)
        if matches:
            return matches[0]
        else:
            f.write('\n' + name)
            return name

def find_image_str(file, x, y, w, h, string):
    correct=grab_data(file, x, y, w, h, False, string).strip()
    if correct != string:
        print("Bad: " + correct)
        return False
    else:
        print("Found: " + correct)
        return True
        
def find_image_num(file, x, y, w, h, num):
    correct=grab_data(file, x, y, w, h, True).strip()
    if correct != num:
        print("Bad: " + str(num))
        return False
    else:
        print("Found: " + str(num))
        return True

def should_be_scaled(height, width):
    return height>1458 and width >2592 and math.isclose(width/height, 1.77777, rel_tol=1e-5)
    
def parse(image_file, output_path):

    # Constants (in % distance from 0,0 of image size)
    SCOREBOARD_X = 0.0491
    SCOREBOARD_Y = 0.0488
    SCOREBOARD_W = 0.1563
    SCOREBOARD_H = 0.0313
    
    MAP_X_BIG = 0.3681
    MAP_Y_BIG = 0.2490
    MAP_W_BIG = 0.0638
    MAP_H_BIG = 0.0131
    
    # Game Scores
    TOPSCORE_X_BIG = 0.2568
    TOPSCORE_Y_BIG = 0.4629
    BOTSCORE_X_BIG = 0.2568
    BOTSCORE_Y_BIG = 0.7642
    
    # Standard Height/Width of game scores
    GAMESCORE_H_BIG = 0.0660
    GAMESCORE_W_BIG = 0.0250
    
    # Standard Height/Width of other scores
    SCORE_H_BIG = 0.0262
    SCORE_W_BIG = 0.0245
    
    TIME_X_BIG = 0.8478
    TIME_Y_BIG = 0.2498
    TIME_W_BIG = 0.0221
    TIME_H_BIG = 0.0131
    
    PLAYER_SCORES_X_BIG = 0.3220
    TOPPLAYER_SCORES_Y_BIG = 0.3057
    BOTPLAYER_SCORES_Y_BIG = 0.5965
    PLAYER_SCORES_W_BIG = 0.5430
    
    # Read File and print out size
    image = cv2.imread(image_file)
    height, width, channels = image.shape
    print(height,width)
        
    # Calculate location of "Big" Scoreboard
    scoreboard_x_scale = round(SCOREBOARD_X * width)
    scoreboard_y_scale = round(SCOREBOARD_Y * height)
    scoreboard_w_scale = round(SCOREBOARD_W * width)
    scoreboard_h_scale = round(SCOREBOARD_H * height)
    
    # Invert a greyscale image
    gray = get_grayscale(image)
    thresh = thresholding(gray)
    #inverted = invert_colors(thresh)
    #cv2.imshow('inverted', inverted)
    
    # Remove dots
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, 8, cv2.CV_32S)
    sizes = stats[1:, -1] #get CC_STAT_AREA component
    img2 = np.zeros((labels.shape), np.uint8)

    for i in range(0, nlabels - 1):
        if sizes[i] >= 8:   #filter small dotted regions
            img2[labels == i + 1] = 255

    inverted = cv2.bitwise_not(img2)

    #cv2.imshow('final', inverted)
    #cv2.waitKey(0)

    if should_be_scaled(height,width) :
        print("scaled down")
        inverted = scale_image(inverted,1458,2592)

    # Check if we are on the big or small scoreboard
    big_scoreboard = find_image_str(inverted, scoreboard_x_scale, scoreboard_y_scale, scoreboard_w_scale, scoreboard_h_scale, "SCOREBOARD")
    
    if big_scoreboard == True:
        print("Using Big Scoreboard")
        
        # Scale locations of items
        map_x_scale = round(MAP_X_BIG * width)
        map_y_scale = round(MAP_Y_BIG * height)
        map_w_scale = round(MAP_W_BIG * width)
        map_h_scale = round(MAP_H_BIG * height)
        
        topscore_x_scale = round(TOPSCORE_X_BIG * width)
        topscore_y_scale = round(TOPSCORE_Y_BIG * height)
        botscore_x_scale = round(BOTSCORE_X_BIG * width)
        botscore_y_scale = round(BOTSCORE_Y_BIG * height)
        gamescore_h_scale = round(GAMESCORE_H_BIG * height)
        gamescore_w_scale = round(GAMESCORE_W_BIG * width)
        score_h_scale = round(SCORE_H_BIG * height)
        score_w_scale = round(SCORE_W_BIG * width)
        
        time_x_scale = round(TIME_X_BIG * width)
        time_y_scale = round(TIME_Y_BIG * height)
        time_w_scale = round(TIME_W_BIG * width)
        time_h_scale = round(TIME_H_BIG * width)
        
        player_scores_x_scale = round(PLAYER_SCORES_X_BIG * width)
        topplayer_scores_y_scale = round(TOPPLAYER_SCORES_Y_BIG * height)
        botplayer_scores_y_scale = round(BOTPLAYER_SCORES_Y_BIG * height)
        player_scores_w_scale = round(PLAYER_SCORES_W_BIG * width)
    
    else:
        print("Using Small Scoreboard")
        print("Not yet supported... returning")
        #TODO... change locations
        return
    
    match_map = grab_data(inverted, map_x_scale, map_y_scale, map_w_scale, map_h_scale, False).strip()
    print("Match Map: " + match_map)

    top_score = grab_data(inverted, topscore_x_scale, topscore_y_scale, gamescore_w_scale, gamescore_h_scale, True).strip()
    print("Top Score: " + str(top_score))
    
    bottom_score = grab_data(inverted, botscore_x_scale, botscore_y_scale, gamescore_w_scale, gamescore_h_scale, True).strip()
    print("Bottom Score: " + str(bottom_score))
    
    time = grab_data(inverted, time_x_scale, time_y_scale, time_w_scale, time_h_scale, False).strip()
    print("Time: " + time)

    top_players = []
    for x in range(10):
        data = grab_data(inverted, player_scores_x_scale, topplayer_scores_y_scale+(x*score_h_scale), player_scores_w_scale, score_h_scale, False)
        if data.strip():
            top_players.append(data.strip().rsplit(' ', 5))
        else:
            break

    bottom_players = []
    for x in range(10):
        data = grab_data(inverted, player_scores_x_scale, botplayer_scores_y_scale+(x*score_h_scale), player_scores_w_scale, score_h_scale, False)
        if data.strip():
            bottom_players.append(data.strip().rsplit(' ', 5))
        else:
            break

    # Autogenerate a match ID to create a unique entry
    match_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b'=').decode('ascii')

    print("Current Dir: " + os.getcwd())
    with open(output_path + '/output.csv', 'a+') as match_file:
        match_writer = csv.writer(
            match_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for p in top_players:
            match_writer.writerow([match_user_name(p[0].strip()),
                                   match_id,
                                   match_map,
                                   isWinner(top_score, bottom_score),
                                   '?',
                                   time,
                                   top_score,
                                   make_int(top_score)+make_int(bottom_score),
                                   make_int(p[1].strip()),
                                   make_int(p[2].strip()),
                                   make_int(p[3].strip()),
                                   make_int(p[4].strip()),
                                   make_int(p[5].strip())])

        for p in bottom_players:
            match_writer.writerow([match_user_name(p[0].strip()),
                                   match_id, match_map,
                                   isWinner(bottom_score, top_score),
                                   '?',
                                   time,
                                   bottom_score,
                                   make_int(top_score)+make_int(bottom_score),
                                   make_int(p[1].strip()),
                                   make_int(p[2].strip()),
                                   make_int(p[3].strip()),
                                   make_int(p[4].strip()),
                                   make_int(p[5].strip())])

        #os.rename(image_file, output_path+match_id+'.png')
    # closing all open windows
    cv2.destroyAllWindows()

# Download attachments from Gmail msgs... either READ, UNREAD or ALL msgs
def download_attachments(write_path,type):
    
    layout = [
        [
            sg.Text("Downloading attachments...", key="-DOWNLOAD-"),
        ],
    ]
        
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # Cannot run "run_local_server" in docker...
            # using run_console instead as page tries to take to localhost
            # inside the docker container that is not accessible from
            # Browser on the host
            #creds = flow.run_local_server(port=49705)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('/home/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    
    # Get messages from GMAIL
    if type != "ALL":
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=type).execute()
    else:
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        
    messages = results.get('messages')
    
    # Count Messagse
    message_count = 0;
    for msg in messages:
        message_count = message_count + 1
        
    if not messages:
        print("No new messages")
    else:
        window = sg.Window("Downloading Attachments", layout)
        event, values = window.Read(timeout=10) # must call after starting window
            
        print("Found " + str(message_count) + " messages." )
        # iterate through all the messages
        download_count = 0
        for msg in messages:
        
            if download_count == 0:
                print("Download " + type)
                print("Downloading messages to " + write_path)
                
            # Get the message from its id
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
          
            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = txt['payload']
                headers = payload['headers']
                internalDate = txt['internalDate']

                for part in txt['payload']['parts']:
                    if part['filename']:
                        download_count = download_count + 1
                        window["-DOWNLOAD-"].update("Downloading " + str(download_count) + " of " + str(message_count))
                        event, values = window.Read(timeout=10)
                        if event == sg.WINDOW_CLOSED or event == 'Quit':
                            break
                        if 'data' in part['body']:
                            data = part['body']['data']
                        else:
                            att_id = part['body']['attachmentId']
                            att = service.users().messages().attachments().get(userId='me', messageId='id',id=att_id).execute()
                            data = att['data']
                        path = write_path + "/" + internalDate + "-" + part['filename']
                        print("Downloading... " + path)
                        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

                        with open(path, 'wb') as f:
                            f.write(file_data)
                                
                # Remove UNREAD as a label so we dont download it again
                service.users().messages().modify(userId='me', id=msg['id'],body={'removeLabelIds': ['UNREAD']}).execute()
                    
            except errors.HttpError as error:
                print("An error occurred: %s' % error")
                
        print("Downloaded " + str(download_count) + " messages.")
        window.close()
        

def make_file_list_inputs(window, values):
    input_path = values["-FOLDERIN-"]
    try:
        # Get list of files in folder
        file_list = os.listdir(input_path)
    except:
        file_list = []

    fnames = [
        f
        for f in file_list
        if os.path.isfile(os.path.join(input_path, f))
        and f.lower().endswith((".png", ".gif"))
    ]
    window["-FILE LIST-"].update(fnames)

# Return image and scale down if necessary
def get_img_data(f, maxsize=(800, 650)):
    img = Image.open(f)
    img.thumbnail(maxsize)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()

def stat_page():
    
    user_list_column = [
        [
            sg.Text("Select Input File"),
            sg.In(size=(25, 1), enable_events=True, key="-INPUTFILE-"),
            sg.FileBrowse(initial_folder="/home"),
        ],
        [
            sg.Text("Select User:")
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(40, 20), key="-USER LIST-"
            )
        ],
    ]

    user_stats_column = [
        [
            sg.Text("Most Wins: ", size=(10,1)), sg.Text("", size=(20,1), key="-MOSTWINS-"),sg.Text("Least Wins: ", size=(10,1)), sg.Text("", size=(20,1), key="-LEASTWINS-"),
        ],
        [
            sg.Text("Most Kills: ", size=(10,1)), sg.Text("", size=(20,1), key="-MOSTKILLS-"),sg.Text("Least Kills: ", size=(10,1)), sg.Text("", size=(20,1), key="-LEASTKILLS-"),
        ],
        [
            sg.Text("Best KD: ", size=(10,1)), sg.Text("", size=(20,1), key="-BESTKD-"),sg.Text("Worst KD: "), sg.Text("", size=(20,1), key="-WORSTKD-"),
        ],
        [
            sg.Text("-------------------------------------------------------------------------"),
        ],
        [
            sg.Text("Kills: ", size=(10,1)), sg.Text("", size=(20,1), key="-KILLS-"), sg.Text("Deaths:", size=(10,1)), sg.Text("", size=(20,1), key="-DEATHS-"),
        ],
        [
            sg.Text("Wins: ", size=(10,1)), sg.Text("", size=(20,1), key="-WINS-"), sg.Text("Losses:", size=(10,1)), sg.Text("", size=(20,1), key="-LOSSES-"),
        ],
        [
            sg.Text("K/D: ", size=(10,1)), sg.Text("", size=(20,1), key="-KD-"),
        ],
        [
            sg.Text("Fav Map: ", size=(10,1)), sg.Text("", key="-FAVMAP-"), sg.Text("Worst Map:", size=(10,1)), sg.Text("", key="-WMAP-"),
        ],
    ]
    
    layout = [
        [
            sg.Column(user_list_column),
            sg.VSeperator(),
            sg.Column(user_stats_column),
        ]
    ]
    
    # Create the window
    window = sg.Window("COD Stats", layout)

    # Data Storage for Stats
    players = []
    kills = dict([])
    deaths = dict([])
    kd = dict([])
    wins = dict([])
    losses = dict([])
        
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "-INPUTFILE-":
            input_file = values["-INPUTFILE-"]

            
            with open(input_file, 'r') as csvfile:
                mycsv = csv.reader(csvfile)
                mycsv = list(mycsv)
    
                for row in mycsv:
                    player = row[0]
                    if player not in players:
                        players.append(player)
                        kills[player] = 0
                        deaths[player] = 0
                        kd[player] = 0
                        wins[player] = 0
                        losses[player] = 0
                    kills[player] = kills[player] + int(row[10])
                    deaths[player] = kills[player] + int(row[11])
                    kd[player] = kills[player]/deaths[player]
                    if row[3] == "TRUE":
                        wins[player] = wins[player] + 1
                    if row[3] == "FALSE":
                        losses[player] = losses[player] + 1
            
            most_kills_player = max(kills, key=kills.get) #returns index of player with most kills
            most_kills_num = kills[most_kills_player]
            window["-MOSTKILLS-"].update(most_kills_player + ": " + str(most_kills_num))
            
            least_kills_player = min(kills, key=kills.get) #returns index of player with most kills
            least_kills_num = kills[least_kills_player]
            window["-LEASTKILLS-"].update(least_kills_player + ": " + str(least_kills_num))
            
            window["-USER LIST-"].update(players)
        elif event == "-USER LIST-":
            # Update Individual Stats when player selected
            player = values["-USER LIST-"][0]
            window["-KILLS-"].update(kills[player])
            window["-DEATHS-"].update(deaths[player])
            window["-KD-"].update("%.2f" % kd[player])
            window["-WINS-"].update(wins[player])
            window["-LOSSES-"].update(losses[player])
    
def launch_gui():
    # Create GUI to chose image file path

    file_list_column = [
        [
            sg.Text("Input Image Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDERIN-"),
            sg.FolderBrowse(initial_folder="/home"),
        ],
        [
            sg.Text("Output Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDEROUT-"),
            sg.FolderBrowse(initial_folder="/home"),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
            )
        ],
        [
            sg.Radio('Unread Emails', "RADIO1", default=True, key="-UNREAD-"),
            sg.Radio('All Emails', "RADIO1", default=False, key="-ALL-"),
        ],
        [
            sg.Button(
                "Download Gmail Photos", enable_events=True, size=(25, 1), key="-DL-"
            )
        ],
        [
            sg.Button(
                "Parse Photos", enable_events=True, size=(25, 1), key="-PARSE-"
            )
        ],
        [
            sg.Button(
                "Stat Form", enable_events=True, size=(25,1), key="-STATS-"
            )
        ],
    ]

    # For now will only show the name of the file that was chosen
    image_viewer_column = [
        [sg.Text("Choose an image from list on left for thumbnail preview:")],
        [sg.Text(size=(80, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
    ]

    # ----- Full layout -----
    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
        ]
    ]

    # Create the window
    window = sg.Window("COD Scoreboard Parser", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # Folder name was filled in, make a list of files in the folder
        if event == "-FOLDERIN-":
            make_file_list_inputs(window, values)
            
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                filename = os.path.join(
                    values["-FOLDERIN-"], values["-FILE LIST-"][0]
                )
                window["-TOUT-"].update(filename)
                window["-IMAGE-"].update(data=get_img_data(filename))
            except:
                pass
        elif event == "-PARSE-":  # Parse Files
            output_path = values["-FOLDEROUT-"]
            input_path = values["-FOLDERIN-"]
            print("Output Path: " + output_path)
            print("Input Path: " + input_path)
            try:
                # Get list of files in folder
                file_list = os.listdir(input_path)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(input_path, f))
                and f.lower().endswith((".png", ".gif"))
            ]
            if not fnames:
                print("No Files Found.")
            else:
                for file in fnames:
                    filename = input_path + "/" + file
                    print("Parse file: " + filename)
                    parse(filename, output_path)
        elif event == "-DL-": # Download photos from gmail
            input_path = values["-FOLDERIN-"]
            if not input_path:
                input_path = "/home"
            print("Downloading attachments to input_path: " + input_path)
            if values["-UNREAD-"] == True:
                type = "is:unread"
            elif values["-ALL-"] == True:
                type = "ALL"
            download_attachments(input_path,type)
            make_file_list_inputs(window, values)
        elif event == "-STATS-":
            stat_page()

    # We exited... close
    window.close()

# Decide if we should launch GUI or run as a script
if sys.argv[1] == "GUI":
    launch_gui()
elif sys.argv[1] == "DL":
    if not sys.argv[2]:
        type = "ALL"
        print("Defaulting to download ALL messages")
    else:
        type = sys.argv[2]
    if not sys.argv[3]:
        type = "/home"
        print("Defaulting to save files to $HOME")
    else:
        path = sys.argv[3]
    download_attachments(path, type)
# just run basic parser through commandline
else:
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    print("Input Path: " + input_path)
    print("Output Path: " + output_path)
    os.chdir(input_path)
    if not input_path:
        print("No input path for arg1")
    files = 0
    for file in glob.glob("*.png"):
        files = files + 1
        print("Parse: " + file)
        parse(file, output_path)
    if files == 0:
        print("No files found")
        list_files = subprocess.run(["ls", "-l"])
