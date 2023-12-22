#!/usr/bin/python
#
# update.py
# updates audiodharma.ai with new raw transcripts
# based off config file showing all talks, for any talk that is not transcribed, download
# the mp3 and then create a transcription via whisper
#
#  command_whisper = f'whisper --verbose False  --model medium {path_mp3} --output_format txt --output_dir {PATH_TMP_OUTPUT}\n'
#
import os
import sys
import json
import urllib.request
import time
from os import path
import subprocess
import time
import datetime
import shutil
from datetime import datetime
import socket
import whisper

from common import URL_MP3_HOST
from common import LOG, getAllTalks, getRawTranscriptPath, getTranscriptPath, getMP3Path, getTalkURL

CountDownloads = 0
CountTranscripts = 0

# this socket is used as a semaphore, to ensure only one instance of update runs at a time
ServerSocket = None
HOST = '127.0.0.1'  
PORT = 12345        


def is_unique_instance():

    global ServerSocket

    try:
        ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        ServerSocket.bind((HOST, PORT))
        return True
    except:
        return False


def talk_download(source_url, path_mp3):

    global CountDownloads

    LOG(f'downloading: {source_url} to {path_mp3}')
    if path.exists(path_mp3):
        LOG('mp3 exists')
        return True

    try:
        response = urllib.request.urlopen(source_url)
    except:
        LOG(f'ERROR: {source_url} not found')
        return False

    data = response.read()
    with open(path_mp3, "wb") as fd:
        fd.write(data)
        CountDownloads += 1

    time.sleep(5.0)
    LOG(f'downloaded: {path_mp3}')

    return True


def talk_transcribe(path_mp3, path_raw_transcript):

    global CountTranscripts

    LOG(f'transcribing: {path_mp3} to: {path_raw_transcript}')
    model = whisper.load_model("medium")
    result = model.transcribe(path_mp3)
    text = result["text"]
    with open(path_raw_transcript, 'w') as fd:
        print(text)
        fd.write(text)

#
# Main
# 
LOG(f'\n\n#############\nupdate.py\nbegin: updating to new transcripts')

if not is_unique_instance():
    LOG("exiting: another instance of update.py is running.")
    exit()

#
# if talk not transcribed, transcribe it
# currently we only do ONE talk at a time, and rely on cron to keep 
# creating new update runs.  we do this to balance load across time
#
list_talks = getAllTalks()
for talk in list_talks:

    if talk['ln'] != 'en':
        continue

    title = talk['title']
    url = talk['url']

    source_url= getTalkURL(talk)
    path_mp3 = getMP3Path(talk)
    path_raw_transcript = getRawTranscriptPath(talk)
    path_transcript = getTranscriptPath(talk)

    # if transcript already exists, skip it
    if path.exists(path_raw_transcript):
        print(f'skipping: {path_raw_transcript}')
        continue

    # download it
    if not talk_download(source_url, path_mp3):
        continue

    # transcribe it
    time_start = time.time()
    talk_transcribe(path_mp3, path_raw_transcript)
    time_end = time.time()
    time_execution = round(time_end - time_start)
    minutes = round(time_execution / 60)
    LOG(f'execution time: {minutes} minutes')

    # for now, just one transcript per run!
    break


LOG(f'complete')
LOG(f'downloads: {CountDownloads}   new transcripts: {CountTranscripts}')
