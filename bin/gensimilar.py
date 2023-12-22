#!/usr/bin/python
#
# For each talk and speaker, generate most similar (and least similar) lists of matches
#
import os
import torch
import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from common import LOG, getAllTalks, getAllSpeakers, getSpeakerSummaryPath, getTalkSummaryPath, getTalkSimilarPath, getSpeakerSimilarPath, DictRankedTalks
from common import VECTOR_COLLECTION_AD_KEYS, VECTOR_COLLECTION_AD_SPEAKERS, VECTOR_COLLECTION_AD_SERIES, QDRANT_SERVER_PORT, PATH_SPEAKER_FILES

MAX_MATCHES = 20 # vector db  max limit on number of matches to return


#
# Main
#
LOG('gensimilar starts')
VectorDB = QdrantClient(host="localhost", port=QDRANT_SERVER_PORT)
VectorizatonModel = SentenceTransformer('all-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')

count_similar = count_different = 0

LOG('gensimilar generating similar talks')
for talk in getAllTalks():

    title = talk['title']
    path_similar = getTalkSimilarPath(talk)
    #if os.path.exists(path_similar): continue

    path_summary_key = getTalkSummaryPath(talk, '.key')
    if not os.path.exists(path_summary_key):
        LOG(f'key not found: {path_summary_key}')
        continue
    with open(path_summary_key) as fd:
        key_text = fd.read()

    # generate most-similar
    #print(key_text)
    key_vector = VectorizatonModel.encode(key_text)
    list_results = VectorDB.search(
        collection_name=VECTOR_COLLECTION_AD_KEYS,
        query_vector=key_vector,
        limit=MAX_MATCHES + 1 # plus one to filter
    )

    list_talks = []
    for result in list_results:

        similar_talk = result.payload
        score = round(result.score, 2)

        url = similar_talk['url']
        if url in DictRankedTalks:
            pop_score = DictRankedTalks[url]['score']
            pop_score_adjustment = pop_score / 10000
            score = score  + pop_score_adjustment
            if score > 0.9: score = 0.90

        similar_talk['score'] = score
        list_talks.append(similar_talk)

    list_talks = sorted(list_talks, key=lambda x: x['score'], reverse=True)

    print(f'generating: {count_similar} {path_similar}')
    data = {}
    with open(path_similar, "w") as fd:
        data['title'] = title
        data['list_elements'] = list_talks
        json.dump(data, fd, indent=4)
        count_similar += 1


LOG('gensimilar generating similar speakers')
for speaker, list_elements in getAllSpeakers():

    print(speaker)
    speakerJSON = {}
    count_talks = len(list_elements)

    summary_long = summary_short = ''
    path_speaker_similar = getSpeakerSimilarPath(speaker)

    path_summary_short = getSpeakerSummaryPath(speaker, '.short')
    path_summary_long = getSpeakerSummaryPath(speaker, '.long')
    path_summary_key = getSpeakerSummaryPath(speaker, '.key')

    with open(path_summary_short, 'r') as fd:
        summary_short = fd.read()
    with open(path_summary_long, 'r') as fd:
        summary_long = fd.read()
    with open(path_summary_key, 'r') as fd:
        key_text = fd.read()

    speakerJSON['title'] = speaker
    speakerJSON['summary_short'] = summary_short
    speakerJSON['summary_long'] = summary_long
    speakerJSON['count_talks'] = count_talks

    # generate most-similar
    speaker_vector = VectorizatonModel.encode(key_text)
    list_results = VectorDB.search(
        collection_name=VECTOR_COLLECTION_AD_SPEAKERS,
        query_vector=speaker_vector,
        limit=10
    )
    print(list_results)

    list_similar_speakers = []
    for result in list_results:

        # similar speaker fields from vector db:  title, talk_count.  
        # now must add in short_summary and the score
        similar_speaker = result.payload
        path_summary_short = getSpeakerSummaryPath(similar_speaker['title'], '.short')
        if not os.path.exists(path_summary_short): continue

        with open(path_summary_short, 'r') as fd:
            similar_summary_short = fd.read()
            similar_speaker['summary_short'] = similar_summary_short

            similar_speaker['score'] = round(result.score, 2)
            list_similar_speakers.append(similar_speaker)

    with open(path_speaker_similar, 'w') as fd:
        speakerJSON['list_elements'] = list_similar_speakers
        json.dump(speakerJSON, fd, indent=4)



LOG('gensimilar completes')
print(f'similar: {count_similar} total new files generated')
print(f'different: {count_different} total new files generated')

