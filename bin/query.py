#!/usr/bin/python
# 
# sophia.py
#
# implements all APIs to access system
# runs as http server on port SOPHIA_SERVER_PORT
#
import os
import datetime
import sys
import json
from urllib.parse import unquote
from urllib.parse import urlparse, parse_qs
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from common import LOG, getAllTalks, getAllSpeakers, getSpeakerSummaryPath, getTalkSummaryPath, textToInteger
from common import ACTIVE_MODEL, QDRANT_SERVER_PORT, SOPHIA_SERVER_PORT, VECTOR_COLLECTION_AD_KEYS, VECTOR_COLLECTION_CACHED_SUMMARIES

MAX_MATCHING_TALKS = 10 # maximum number of talks to return when matching on a specific query




def vectorizeText(text):

    text_vector = VectorizatonModel.encode(text)
    return False, text_vector.tolist()


#
# get the talks the most closely match the query, in intent
#
def getVecDBMatchingTalks(query):

    error, query_vector = vectorizeText(query)
    if error: 
        return []

    list_results = VectorDB.search(
        collection_name=VECTOR_COLLECTION_AD_KEYS,
        query_vector=query_vector,
        limit=MAX_MATCHING_TALKS
    )

    list_talks = []
    for result in list_results:
        score = round(result.score,2)
        result.payload['score'] = score
        list_talks.append(result.payload)

    #response = json.dumps(list_talks)
    #return response
    return list_talks 


#
# main
#
VectorDB = QdrantClient(host="localhost", port=QDRANT_SERVER_PORT)
VectorizatonModel = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')


if len(sys.argv) > 1:
    query = sys.argv[1]
    list_talks = getVecDBMatchingTalks(query)
    print('\n\n\n')
    #print(list_talks)
    for talk in list_talks:
        title = talk['title']
        url = talk['url']
        speaker = talk['speaker']
        date =  talk['date']
        score =  talk['score']

        mp3_name =  os.path.basename(urlparse(url).path)
        path_summary_key = getTalkSummaryPath(talk, '.key')
        with open(path_summary_key) as fd:
            key_text = fd.read()

        print(f'{date} {title} {speaker} {score} \n{mp3_name}\n{key_text}')
        print('----------')
else:
    print('No query')



