#!/usr/bin/python
#
# create a json file for each talk, capturing all of talk metadata
# these files are stored in PATH_TALK_FILES 
#
# also create section lists of talks, each list MAX_TALK_PER_SECTION in length
# these are the list of talks that are presented to the UI, for pagination
# these lists are stored in PATH_INDEX_FILES
#
import os
import json
from common import  URL_MP3_HOST
from common import  LOG, getAllTalks, getIndexPath, getTranscriptPath, getTalkSummaryPath, getTalkPath, getSpeakerImageURL, writeJSONData


MAX_TALK_PER_SECTION = 1000
TotalTalks = 0


def convert_to_human_readable(date_string):

    date_obj = datetime.strptime(date_string, '%Y.%m.%d')
    human_readable_date = date_obj.strftime('%b %dth, %Y')
    return human_readable_date

#
# Main
#
LOG('gentalk starts')

list_index_sections = []
list_section_talks = []
for talk in getAllTalks():

    url = talk['url']
    #talk['url'] = URL_MP3_HOST + url

    file_mp3 = os.path.basename(url)
    path_talk =  getTalkPath(file_mp3)
    path_summary_brief = getTalkSummaryPath(talk, '.brief')
    path_summary_long = getTalkSummaryPath(talk, '.long')
    path_transcript = getTranscriptPath(talk)

    print('filter: ', url)
    if not os.path.exists(path_summary_brief): 
        continue
    if not os.path.exists(path_summary_long): 
        continue
    if not os.path.exists(path_transcript): 
        continue

    with open(path_summary_brief) as fd:
        talk['summary_brief'] = fd.read()
    with open(path_summary_long) as fd:
        talk['summary_long'] = fd.read()
    with open(path_transcript) as fd:
        talk['transcript'] = fd.read()

    url_image_speaker = getSpeakerImageURL(talk['speaker'])
    talk['url_image_speaker'] = url_image_speaker

    # now store the talk json
    with open(path_talk, "w") as fd:
        print(f'writing: {path_talk}')
        json.dump(talk, fd, indent=4)

    TotalTalks += 1

    # add talk to a talk section (used by UI for pagination when listing all talks)
    del talk['transcript']  # very large, don't need in sections
    del talk['summary_long']  # very large, don't need in sections
    list_section_talks.append(talk)
    if len(list_section_talks)  == MAX_TALK_PER_SECTION:
        list_index_sections.append(list_section_talks)
        list_section_talks = []

# output all the talk sections
for idx, list_index_talks in enumerate(list_index_sections):

    section = idx * MAX_TALK_PER_SECTION
    path_index_talks = getIndexPath('talks', str(section))
    writeJSONData(path_index_talks, 'Talks', '', list_index_talks)


LOG('gentalk completes')
LOG(f'total talks: {TotalTalks}')

