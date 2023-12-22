#!/usr/bin/python
import sys
import os
import MySQLdb as mdb
import json
import random
import operator
import datetime
import time

# these configs are read and used by this program
PATH_CONFIG_JSON = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON'
PATH_RECOMMENDED_TALKS = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/RECOMMENDED.JSON'
PATH_CHRISTOPHER_TALKS = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CHRISTOPHER.JSON'

# the final product
PATH_RANKED_TALKS = '/var/www/audiodharma/httpdocs/config/RANKEDTALKS.JSON'

FileNameToTalk = {}
RecommendedTalks = []
ChristopherTalks = []

# score values
SCORE_PLAYED = 1
SCORE_SHARED = 3
SCORE_RECOMMENDED = 200
SCORE_CHRISTOPHER = 420
SCORE_CHRISTOPHER = 520
SCORE_NON_GIL_LONG = 600
SCORE_NON_GIL_MEDIUM = 1.5
SCORE_NON_GIL_SHORT = 1

ListAllTalks = []
ListRankedTalks = []
DictFileNameScore = {}


def scoreTalk(filename, score):

    global DictFileNameScore

    if filename in DictFileNameScore:
        DictFileNameScore[filename] += score
    else:
        DictFileNameScore[filename] = score



#
#
# Main
#

# read in configs
try:
    with open(PATH_CONFIG_JSON,'r') as fd:
        ListAllTalks  = json.load(fd)['talks']
        for talk in ListAllTalks:
            filename = talk['url'].rsplit('/', 1)[-1]
            FileNameToTalk[filename] = talk

except:
    sys.exit(1)

try:
    with open(PATH_RECOMMENDED_TALKS,'r') as fd:
        RecommendedTalks  = json.load(fd)
except:
    sys.exit(1)

try:
    with open(PATH_CHRISTOPHER_TALKS,'r') as fd:
        ChristopherTalks  = json.load(fd)
except:
    sys.exit(1)


# rank all talks
try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad')
    cur = con.cursor()

    query = "SELECT filename FROM actions WHERE operation=\"PLAYTALK\""
    cur.execute("SELECT filename FROM actions WHERE operation=\"PLAYTALK\"")
    rows = cur.fetchall()
    talks_played = [i[0] for i in rows]

    query = "SELECT filename FROM actions WHERE operation=\"SHARETALK\""
    cur.execute(query);
    rows = cur.fetchall()
    talks_shared = [i[0] for i in rows]

    for filename in talks_played:
        scoreTalk(filename, SCORE_PLAYED)
    for filename in talks_shared:
        scoreTalk(filename, SCORE_SHARED)

    for filename, score in DictFileNameScore.items():
        if filename in RecommendedTalks:
            DictFileNameScore[filename] += SCORE_RECOMMENDED
        if filename in ChristopherTalks:
            DictFileNameScore[filename] += SCORE_CHRISTOPHER
        if 'Gil' not in filename:
            DictFileNameScore[filename] += SCORE_NON_GIL_LONG


    for talk in ListAllTalks:
        rankedTalk = {}
        url = talk['url']
        filename = os.path.basename(url)
        if filename not in DictFileNameScore:
            print(f'missing: {filename}')
            continue
        score = DictFileNameScore[filename]
        rankedTalk['title'] = talk['title']
        rankedTalk['url'] = talk['url']
        rankedTalk['score'] = score
        ListRankedTalks.append(rankedTalk)

    ListRankedTalks = sorted(ListRankedTalks, key=lambda x: x['score'], reverse=True)

    con.close()

except:
    sys.exit(1)


with open(PATH_RANKED_TALKS, 'w') as fd:
    json.dump(ListRankedTalks, fd, indent=4)


print("Done")


