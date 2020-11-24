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


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def invert_colors(image):
    return cv2.bitwise_not(image)

def grab_data(image, X, Y, W, H, isNum, dataname=""):
    # --psm 6, 7
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_blacklist=&@'
    if isNum:
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:'

    crop_img = image[Y:Y+H, X:X+W]
    if dataname.strip():
        cv2.imshow(dataname, crop_img)
        cv2.waitKey(0)
    return pytesseract.image_to_string(crop_img, config=custom_config)


def isWinner(mine, other):
    return str(int(mine.strip()) > int(other.strip()))


def make_int(str_num):
    return int(str_num.replace('o', '0').replace('a', '0').replace('O', '0').replace('l', '1').replace('L', '1'))


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


def parse(image_file, output_path):
    image = cv2.imread(image_file)

    gray = get_grayscale(image)
    # cv2.imshow('gray', gray)
    # cv2.waitKey(0)
    thresh = thresholding(gray)
    # cv2.imshow('thresh', thresh)
    # cv2.waitKey(0)
    inverted = invert_colors(thresh)
    cv2.imshow('inverted_thresh', inverted)
    cv2.waitKey(0)


    correct=grab_data(inverted, 122, 67, 412, 61, False,"scoreboard").strip()
    print(correct)
    if correct != "SCOREBOARD":
        return

    top_score = grab_data(inverted, 560, 670, 192, 103, True).strip()
    print(top_score)
    bottom_score = grab_data(inverted, 554, 1110, 190, 103, True).strip()
    print(bottom_score)
    match_map = grab_data(inverted, 941, 355, 491, 40, False,).strip()
    print(match_map)
    time = grab_data(inverted, 1779, 354, 481, 40, True).strip()
    print(time)

    top_players = []
    for x in range(10):
        data = grab_data(inverted, 832, 447+(x*40), 1414, 38, False)
        if data.strip():
            top_players.append(data.strip().rsplit(' ', 5))
        else:
            break

    print(top_players)

    bottom_players = []
    for x in range(10):
        data = grab_data(inverted, 832, 871+(x*40), 1414, 38, False)
        if data.strip():
            bottom_players.append(data.strip().rsplit(' ', 5))
        else:
            break

    print(bottom_players)

    match_id = base64.urlsafe_b64encode(
        uuid.uuid3().bytes).rstrip(b'=').decode('ascii')

    print(os.getcwd())
    with open(output_path + 'output.csv', 'a+') as match_file:
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

        os.rename(image_file, output_path+match_id+'.png')
    # closing all open windows
    cv2.destroyAllWindows()


input_path = sys.argv[1]
output_path = sys.argv[2]
print(input_path)
print(output_path)
# os.chdir(input_path)
for file in glob.glob(input_path+"*.png"):
    parse(file, output_path)
