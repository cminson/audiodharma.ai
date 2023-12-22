#!/usr/bin/python
#
#
import os
import sys
import json
import string
import re
from common import  getAllSpeakers, getAllTalks, getTalkSummaryPath


#
# Main
#

set_keywords = set()
print('makekeywords starts')

translator = str.maketrans('', '', string.punctuation)

for speaker, _ in getAllSpeakers():

    print(speaker)
    speaker = speaker.translate(translator)
    list_words = speaker.split()
    for word in list_words:
        if len(word) > 2:
            set_keywords.add(word.lower())


for talk in getAllTalks():

    title = talk['title']
    url = talk['url']
    print(title)
    title = re.sub(r'\d+', '', title)

    text = title.translate(translator)
    list_words = text.split()
    for word in list_words:
        if len(word) > 2:
            set_keywords.add(word.lower())

    path_summary_long = getTalkSummaryPath(talk, '.long')
    if not os.path.exists(path_summary_long):
        print(f'skipping: {path_summary_long}')
        continue

    with open(path_summary_long) as fd:
        text = fd.read()
    text = text.translate(translator)
    list_words = text.split()
    for word in list_words:
        if len(word) > 2:
            set_keywords.add(word.lower())



with open('../config/KEYWORDS.JSON', 'w') as fd:

    json.dump(list(set_keywords), fd, indent=4)




