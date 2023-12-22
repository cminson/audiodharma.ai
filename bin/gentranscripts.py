#!/usr/bin/python3
#
# clean up all raw transcript files (those converted directly from mp3s)
# operates on all files starting with 'raw" in ./data/transcripts
#
# for every raw transcript, create a normalized transcript file
# this normalized transcript file is the text that  will be presented to the UI
#

import os
import json
import random
from common import  LOG, getAllTalks, getAllTranscripts, writeTextData


MIN_TRANSCRIPT_LINES = 5  # transcripts must be at least this long
MIN_LINE_LENGTH = 5     # and a line must be at least this long
MAX_LINE_LENGTH = 1500  # but no bigger

# various cruft we want to filter out
EXCLUSIONS = {'tanya', 'laura', 'computer', 'jennifer', 'zoom',  'chris', 'ines', 'recording', 'insight meditation center', 'imc', 'fronsdal', 'adudioharma', 'irc', 'please visit our website', 'audiodherma.org' , 'audioderma', 'the following talk was given', 'can you hear me', 'good morning', 'thank you', 'www', 'globalonenessprojec', '[silence]', '[bell]', '[blank_audio]', '[silence]', '[speaking in foreign language]' '(wind blowing)'}
LINES_IN_PARAGRAPH = [5, 5, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 10, 10, 12]

TotalNewTranscripts = 0
TotalTranscripts = 0
TotalSkippedTranscripts = 0
ListSkippedTranscripts = []


#
# Main
#
LOG('gentranscripts starts')

# create text from every transcript
for idx, (talk, path_transcript_raw, path_transcript) in enumerate(getAllTranscripts()):

    TotalTranscripts += 1

    if os.path.exists(path_transcript):
        #print(f'Already exists: {path_transcript}')
        continue

    # get the transcript, and clean up the text
    with open(path_transcript_raw, "r", encoding='latin-1') as fd:
        text = fd.read()
        text = text.replace('\n', '')

    text = text.replace('.', '.\n')
    text = text.replace('?', '?\n')
    text = text.replace('!', '!\n')
    text = text.replace('- ', '\n')
    list_lines = text.split('\n')

    # filter out transcripts with little data
    if len(list_lines) < MIN_TRANSCRIPT_LINES: 
        TotalSkippedTranscripts += 1
        ListSkippedTranscripts.append(path_transcript_raw)
        continue


    # filter out too-short lines and exclusions
    tmp = []
    for line in list_lines:
        if len(line) < MIN_LINE_LENGTH: continue
        if any(exclusion.lower() in line.lower() for exclusion in EXCLUSIONS): continue
        tmp.append(line)
    list_lines = tmp

    # filter out repeat lines
    list_lines = [item for item, next_item in zip(list_lines, list_lines[1:] + [None]) if item != next_item]

    # generate the actual text file in simple HTML with random paragraph breaks
    line_count = 0
    text = ''
    lines_in_paragraph = random.choice(LINES_IN_PARAGRAPH)
    for line in list_lines:
        line_count += 1
        text = text + line + ' '
        if line_count > lines_in_paragraph:
            text += "\n<p>\n"
            lines_in_paragraph = random.choice(LINES_IN_PARAGRAPH)
            line_count = 0

    # output this text
    print(f'new transcript: {path_transcript}')
    writeTextData(path_transcript, text)

    TotalNewTranscripts += 1

LOG(f'total transcripts: {TotalTranscripts}')
LOG(f'new: {TotalNewTranscripts}  skipped: {TotalSkippedTranscripts}')
LOG('gentranscripts completes')





