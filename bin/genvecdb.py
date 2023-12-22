#!/usr/bin/python
#
# Generate embedding vectors for all data objects.
# These vectors are stored in an instance of qdrant running at QDRANT_SERVER_PORT
#
import os
import sys
import json
import torch
import hashlib

from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta
from tqdm.notebook import tqdm

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from common import LOG, getAllTalks, getAllSpeakers, getSpeakerSummaryPath, getTalkSummaryPath, textToInteger
from common import VECTOR_COLLECTION_AD_KEYS, VECTOR_COLLECTION_AD_SPEAKERS, VECTOR_COLLECTION_AD_SERIES, VECTOR_COLLECTION_CACHED_SUMMARIES, QDRANT_SERVER_PORT, URL_MP3_HOST


VECTOR_SIZE = 384  # vector length of all-MiniLM-L6-v2
BATCH_SIZE = 100


MP3TalkDict ={}
ListKeyText = []
ListKeyVectors = []
ListKeyTalks = []
ListVectorTalks = []



def collectionExists(name_collection):

    try:
        collection_info = VectorDB.get_collection(collection_name=VECTOR_COLLECTION_AD_KEYS)
    except:
        return False

    return True



#
# Main
#
LOG('gendb starts')


ResetCollections = True

VectorDB = QdrantClient(host="localhost", port=QDRANT_SERVER_PORT)
VectorizatonModel = SentenceTransformer('all-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')  


if ResetCollections:

    LOG(f'creating collection: {VECTOR_COLLECTION_AD_KEYS}')
    VectorDB.recreate_collection(
        collection_name=VECTOR_COLLECTION_AD_KEYS,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    LOG(f'creating collection: {VECTOR_COLLECTION_AD_SPEAKERS}')
    VectorDB.recreate_collection(
        collection_name=VECTOR_COLLECTION_AD_SPEAKERS,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    LOG(f'creating collection: {VECTOR_COLLECTION_AD_SERIES}')
    VectorDB.recreate_collection(
        collection_name=VECTOR_COLLECTION_AD_SERIES,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    LOG(f'creating collection: {VECTOR_COLLECTION_CACHED_SUMMARIES}')
    VectorDB.recreate_collection(
        collection_name=VECTOR_COLLECTION_CACHED_SUMMARIES,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )


list_speaker = []
list_speaker_key = []
for speaker, list_talks in getAllSpeakers():

    path_summary_key = getSpeakerSummaryPath(speaker, '.key')
    speaker_key = ''
    if os.path.exists(path_summary_key):
        with open(path_summary_key, 'r') as fd:
            speaker_key = fd.read()

    list_speaker.append({'title': speaker, 'count_talks': len(list_talks)})
    list_speaker_key.append(speaker_key)

    count = len(list_talks)
    print(f'{speaker} {count} {speaker_key}')


# vectorize all these  speakers, store in database
list_vectors = VectorizatonModel.encode([
    speaker_key for speaker_key in list_speaker_key
], show_progress_bar=False)


list_vector_speakers = []
for idx, vector in enumerate(list_vectors):
    list_vector_speakers.append((vector, list_speaker[idx]))


num_vectors = len(list_vector_speakers)
LOG(f'store vectors {num_vectors} into database')


for i in range(0, num_vectors, BATCH_SIZE):
    print('Batch: ', i)
    batch_vectors = list_vector_speakers[i:i + BATCH_SIZE]
    batch_points = [
        PointStruct(
            id=textToInteger(vector_speaker[1]['title']),
            vector=vector_speaker[0].tolist(),
            payload=vector_speaker[1]
        )
        for idx, vector_speaker in enumerate(batch_vectors)
    ]

    VectorDB.upsert(
        collection_name=VECTOR_COLLECTION_AD_SPEAKERS,
        points=batch_points
    )


#DEV 
"""
path_speaker_key = '/var/www/audiodharma/httpdocs/data/summaries/speaker.Bruce Freedman.key'
with open(path_summary_key, 'r') as fd:
    speaker_key = fd.read()
print(speaker_key)
speaker_vector = VectorizatonModel.encode(speaker_key)
list_results = VectorDB.search(
        collection_name=VECTOR_COLLECTION_AD_SPEAKERS,
        query_vector=speaker_vector,
        limit=10
)
print(list_results)
print("list")
for speaker in list_results:
    #print(speaker.payload)
    score = speaker.score
    print(score, speaker)
    #score = speaker.payload['score']
    #print(f'{speaker} {score}')
"""


collection_info = VectorDB.get_collection(collection_name=VECTOR_COLLECTION_AD_SPEAKERS)
print(f'VECTOR_COLLECTION_QUOTES: {collection_info}')


#
# vectorize all talks
#
set_vectors = set()
dict_vectors = {}
list_talks = []

all_talks = getAllTalks()
for talk in all_talks:

    url = talk['url']
    title = talk['title']
    speaker = talk['speaker']
    file_mp3 = os.path.basename(url)

    path_summary_long = getTalkSummaryPath(talk, '.long')
    path_summary_brief = getTalkSummaryPath(talk, '.brief')
    path_summary_key = getTalkSummaryPath(talk, '.key')

    if not os.path.exists(path_summary_long):
        continue
    if not os.path.exists(path_summary_brief):
        continue
    if not os.path.exists(path_summary_key):
        continue

    # store summaries as metainfo in vector db
    with open(path_summary_long) as fd:
        long_text = fd.read()
        talk['summary_long'] = long_text

    with open(path_summary_brief) as fd:
        brief_text  = fd.read()
        talk['summary_brief'] = brief_text

    with open(path_summary_key) as fd:
        key_text  = fd.read()
        talk['summary_key'] = key_text


    # create parallel lists of keys/talks
    key_text = f'{speaker} {key_text} {speaker} '
    print(key_text)
    ListKeyText.append(key_text)
    ListKeyTalks.append(talk)

    print(talk)
    print(key_text)


# vectorize all these key. then create
# a list (ListVectorTalks) which contains tuples of form:  <key_vector, talk_metadata>
print('creating talk vectors')
list_vectors = VectorizatonModel.encode([
    key_text for key_text in ListKeyText
], show_progress_bar=False)

print('Vectors encoded: ', len(list_vectors))

for idx, vector in enumerate(list_vectors):
    ListVectorTalks.append((vector, ListKeyTalks[idx]))


# feed this list is then fed into vector database
print('store vectors into database')
num_vectors = len(ListVectorTalks)

for i in range(0, num_vectors, BATCH_SIZE):
    print('Batch: ', i)
    batch_vectors = ListVectorTalks[i:i + BATCH_SIZE]
    batch_points = [
        PointStruct(
            id=textToInteger(os.path.basename(vector_talk[1]['url'])),
            vector=vector_talk[0].tolist(),
            payload=vector_talk[1]
        )
        for idx, vector_talk in enumerate(batch_vectors)
    ]

    VectorDB.upsert(
        collection_name=VECTOR_COLLECTION_AD_KEYS,
        points=batch_points
    )

key_count = len(ListKeyTalks)
collection_info = VectorDB.get_collection(collection_name=VECTOR_COLLECTION_AD_KEYS)

v = VectorizatonModel.encode('current latest')
list_results = VectorDB.search(
        collection_name=VECTOR_COLLECTION_AD_KEYS,
        query_vector=v,
        limit=10
)
for result in list_results[:10]:
    talk = result.payload
    title = talk['title']
    speaker = talk['speaker']
    date = talk['date']
    print(f'{date} {title} {speaker}')


print(f'VECTOR_COLLECTION_AD_KEYS: {collection_info}')
LOG(f'collection:  {VECTOR_COLLECTION_AD_KEYS}  total keys inserted: {key_count}')
LOG('gendb completes')
