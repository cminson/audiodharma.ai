#!/usr/bin/python
#
# create a json file for each speaker, capturing all of speaker  metadata
# these files are stored in PATH_SPEAKER_FILES 
#
import os
import sys
import json
import re
from common import  LOG, getAllTalks, getIndexPath, getTalkSummaryPath, getSpeakerPath, getAllSpeakers, getSpeakerSummaryPath, writeJSONData


#
# Main
#
print('genspeakers starts')

list_speakers = []
for speaker, list_talks in getAllSpeakers():

    print(speaker)
    if len(list_talks) == 0: continue

    summary_text_short = summary_text_long = ''
    path_summary_long = getSpeakerSummaryPath(speaker, '.long')
    path_summary_short = getSpeakerSummaryPath(speaker, '.short')

    if os.path.exists(path_summary_long):
        with open(path_summary_long, 'r') as fd:
            summary_text_long = fd.read()
    if os.path.exists(path_summary_short):
        with open(path_summary_short, 'r') as fd:
            summary_text_short = fd.read()

    #file_name_speaker = speaker.replace(' ', '') 
    path_speaker = getSpeakerPath(speaker)

    with open(path_speaker, 'w') as fd:

        # output speaker file
        data = {}
        data['title'] = speaker
        data['date'] = list_talks[0]['date']
        data['summary_short'] = summary_text_short
        data['summary_long'] = summary_text_long
        data['list_elements'] = list_talks
        data['count_talks'] = len(list_talks)
        print(f'{path_speaker}')
        json.dump(data, fd, indent=4)

        # add data to index speaker
        data_index = {}
        data_index['title'] = speaker
        data_index['date'] = list_talks[0]['date']
        data_index['summary_short'] = summary_text_short
        data_index['count_talks'] = len(list_talks)
        list_speakers.append(data_index)

# generate a json file indexing all speakers
data_index = {}
list_speakers_sorted_name = sorted(list_speakers, key=lambda x: x['title'])
list_speakers_sorted_date = sorted(list_speakers, key=lambda x: x['date'])
list_speakers_sorted_date.reverse()
data_index['sorted_alphabetically'] = list_speakers_sorted_name
data_index['sorted_by_talk_date'] = list_speakers_sorted_date

path_index_speakers = getIndexPath('speakers', '')
writeJSONData(path_index_speakers, 'Speakers', '', data_index)



LOG('genspeakers completes')
total_speakers = len(list_speakers)
LOG(f'total speakers generated: {total_speakers}')


