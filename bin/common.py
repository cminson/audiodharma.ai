#!/usr/bin/python
#
# common functions and globals for audiohdarma.ai
#
import os
import sys
import json
import logging
import string
import hashlib
import socket



BASE_PATH = '/var/www/audiodharma/httpdocs/'
BASE_URL = 'https://www.audiodharma.ai/'

PATH_OPENAI_KEYS =  '/var/www/audiodharma/KEYS/OPENAI.KEYS'

PATH_AUDIODHARMA_LOG = BASE_PATH + 'LOGS/AD.LOG'
PATH_TRANSCRIPTS = BASE_PATH + 'data/transcripts'
PATH_INDEX_FILES = BASE_PATH + 'data/index'
PATH_TEXT_FILES = BASE_PATH + 'data/text'
PATH_SUMMARY_FILES =  BASE_PATH + 'data/summaries'
PATH_SIMILAR_FILES = BASE_PATH + 'data/similar'
PATH_DIFFERENT_FILES = BASE_PATH + 'data/different'
PATH_SERIES_FILES = BASE_PATH + 'data/series'
PATH_SPEAKER_FILES = BASE_PATH + 'data/speakers'
PATH_TALK_FILES = BASE_PATH + 'data/talks'
PATH_TMP_FILES = BASE_PATH + 'data/tmp'
PATH_MP3_FILES = BASE_PATH + 'data/mp3'
PATH_BIOGRAPHY_FILES = BASE_PATH + 'data/biographies'
PATH_RANKED_TALKS = BASE_PATH + 'config/RANKEDTALKS.JSON'
PATH_RULE_ACTIONS = BASE_PATH + 'config/RULES.JSON'
PATH_CONFIG_TALKS = BASE_PATH + 'config/ALLTALKS.JSON'
PATH_KEYWORDS = BASE_PATH + 'config/KEYWORDS.JSON'

PATH_SPEAKER_IMAGES =  BASE_PATH + 'resources/teachers'
URL_IMAGE_SPEAKER  = BASE_URL + 'resources/teachers/'
SPEAKER_IMAGE_DEFAULT =  'defaultSpeakerImage.png'


VECTOR_COLLECTION_AD_KEYS = 'VECTOR_COLLECTION_AD_KEYS'  # collection of keys -> talks
VECTOR_COLLECTION_AD_SPEAKERS = 'VECTOR_COLLECTION_AD_SPEAKERS' # collection of keys -> speakers
VECTOR_COLLECTION_AD_SERIES = 'VECTOR_COLLECTION_AD_SERIES' # collection of keys -> series
VECTOR_COLLECTION_CACHED_SUMMARIES = 'VECTOR_COLLECTION_CACHED_SUMMARIES' # collection of keys -> summaries

MIN_TRANSCRIPT_SIZE = 500

ACTIVE_MODEL = 'gpt-3.5-turbo'
HOST = '127.0.0.1'
QDRANT_SERVER_PORT = 6333  # QDrant handles all vector operations
SOPHIA_SERVER_PORT = 3022  # where this service (sophia) runs


URL_MP3_HOST = 'https://audiodharma.us-east-1.linodeobjects.com/talks'


FILTER_WORDS = set(['shares', 'discuss', 'emphasizes', 'tell', 'gap', 'conducting', 'like', 'take', 'but', 'if', 'it', 'in', 'some', 'us', 'up', 'your', 'from', 'this', 'for', 'as', 'to', 'through', 'on', 'were', 'to', 'we', 'are', 'i', 'the', 'and', 'an', 'a', 'in', 'is', 'of', 'not', 'was', 'that', 'or', 'than', 'it', 'is', 'so', 'try', 'can', 'stay', 'also', 'by', 'at', 'its', 'how', 'come', 'which', 'with', 'let', 'go', 'their', 'be', 'into', 'talk', 'recent', 'visit', 'audiodharam.org', 'IMC', 'audioderma.org', 'maybe', 'our', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", "recent", "recently", "current"])


def LOG(text):

    #now = datetime.datetime.now()
    #date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    print(text)
    logging.info(text)


def configureOpenAIKey():

    with open(PATH_OPENAI_KEYS) as fd:
        lines = fd.readlines()
        key = lines[0].rstrip()
    if not key:
        LOG(f'Error: OPENAI_API_KEY not found')

    return key
    

def getTalkURL(talk):

    url = talk['url']
    return URL_MP3_HOST + url


# return all english-language talks
def getAllTalks():

    responseJSON = {}

    if not os.path.exists(PATH_CONFIG_TALKS): return responseJSON

    with open(PATH_CONFIG_TALKS,'r') as fd:
        config = json.load(fd)
        responseJSON = [talk for talk in config['talks'] if talk['ln'] == 'en']


    return responseJSON


def getTalkJSON(file_mp3, _):

    responseJSON = {}

    path_talk = getTalkPath(file_mp3)
    if not os.path.exists(path_talk): return responseJSON

    with open(path_talk, 'r') as fd:
        responseJSON =  json.load(fd)

    return responseJSON


def getAllSpeakers():

    list_talks = []
    list_speakers = []
    with open(PATH_CONFIG_TALKS,'r') as fd:
        config = json.load(fd)
        list_talks = config['talks']

    dict_speakers = {}
    for talk in list_talks:
        speaker = talk['speaker']
        if speaker not in dict_speakers: 
            dict_speakers[speaker] = []

        file_mp3 = os.path.basename(talk['url'])
        path_talk = getTalkPath(file_mp3)
        if not os.path.exists(path_talk): 
            #LOG(f'ERROR: no talk {path_talk}')
            continue

        with open(path_talk, 'r') as fd:
            full_talk =  json.load(fd)

        del full_talk['summary_long']
        del full_talk['transcript']
        dict_speakers[speaker].append(full_talk)

    list_speakers = list(dict_speakers.items())
    return list_speakers


def getSpeakerImageURL(speaker):

    image_speaker = f'{speaker}.png'
    path_image_speaker = os.path.join(PATH_SPEAKER_IMAGES, image_speaker)
    if os.path.exists(path_image_speaker) == False:
        image_speaker = SPEAKER_IMAGE_DEFAULT

    url_image_speaker = URL_IMAGE_SPEAKER + image_speaker
    return url_image_speaker


def getAllSeries():

    list_talks = []
    list_series = []
    with open(PATH_CONFIG_TALKS,'r') as fd:
        config = json.load(fd)
        list_talks = config['talks']

    dict_series = {}
    for talk in list_talks:
        series = talk['series']
        series = series.replace('/', '.')

        if series not in dict_series: 
            dict_series[series] = []

        file_mp3 = os.path.basename(talk['url'])
        path_talk = getTalkPath(file_mp3)
        if not os.path.exists(path_talk): 
            #LOG(f'ERROR: no talk {path_talk}')
            continue

        with open(path_talk, 'r') as fd:
            full_talk =  json.load(fd)

        del full_talk['summary_long']
        del full_talk['transcript']
        dict_series[series].append(full_talk)

    list_series = list(dict_series.items())
    return list_series



def getAllTranscripts():

    list_transcripts = []
    list_talks = []

    with open(PATH_CONFIG_TALKS,'r') as fd:
        config = json.load(fd)
        list_talks = config['talks']

    for talk in list_talks:

        file_mp3 = os.path.basename(talk['url'])

        transcript_raw = 'raw.' + file_mp3.replace('.mp3', '.txt')
        transcript = 'transcript.' + file_mp3.replace('.mp3', '.txt')
        path_transcript_raw = os.path.join(PATH_TRANSCRIPTS, transcript_raw)
        path_transcript = os.path.join(PATH_TRANSCRIPTS, transcript)

        if not os.path.exists(path_transcript_raw): continue
        if os.path.getsize(path_transcript_raw) < MIN_TRANSCRIPT_SIZE: continue

        list_transcripts.append((talk, path_transcript_raw, path_transcript))

    return list_transcripts


def getIndexPath(name, section):

    if section:
        index_name = 'index.' + name + '.' + section + '.json'
    else:
        index_name = 'index.' + name + '.json'
    path_index = os.path.join(PATH_INDEX_FILES, index_name)

    return path_index


def getTalkPath(file_mp3):

    talk_name = 'talk.' + file_mp3.replace('.mp3', '.json')
    path_talk = os.path.join(PATH_TALK_FILES, talk_name)

    return path_talk


def getSpeakerPath(speaker):

    file_speaker = 'speaker.' + speaker + '.json'
    path_speaker = os.path.join(PATH_SPEAKER_FILES, file_speaker)

    return path_speaker


def getSeriesPath(series):

    file_series = 'series.' + series + '.json'
    path_series = os.path.join(PATH_SERIES_FILES, file_series)

    return path_series


def getMP3Path(talk):

    file_mp3 = os.path.basename(talk['url'])
    path_mp3 = os.path.join(PATH_MP3_FILES, file_mp3)

    return path_mp3


def getTMPPath(talk):

    return PATH_TMP_FILES


def getRawTranscriptPath(talk):

    file_mp3 = os.path.basename(talk['url'])
    file_raw_transcript = 'raw.' + file_mp3.replace('.mp3', '.txt')
    path_raw_transcript = os.path.join(PATH_TRANSCRIPTS, file_raw_transcript)

    return path_raw_transcript


def getTranscriptPath(talk):

    file_mp3 = os.path.basename(talk['url'])
    file_transcript = 'transcript.' + file_mp3.replace('.mp3', '.txt')
    path_transcript = os.path.join(PATH_TRANSCRIPTS, file_transcript)

    return path_transcript


def getTalkSimilarPath(talk):

    file_similar = 'talk.sim.' + os.path.basename(talk['url']) + '.json'
    path_similar_talks = os.path.join(PATH_SIMILAR_FILES, file_similar)

    return path_similar_talks


def getTalkNameSimilarPath(file_mp3):

    file_similar = 'talk.sim.' + file_mp3  + '.json'
    path_similar_talks = os.path.join(PATH_SIMILAR_FILES, file_similar)

    LOG(f'getTalkNameSimilarPath returns {path_similar_talks}')
    return path_similar_talks


def getSpeakerSimilarPath(speaker):

    file_similar = 'speaker.sim.' + speaker + '.json'
    path_similar_speakers = os.path.join(PATH_SIMILAR_FILES, file_similar)

    return path_similar_speakers


def getTalkSummaryPath(talk, suffix):

    url = talk['url']
    file_mp3 = os.path.basename(url)
    file_summary = 'talk.' + file_mp3.replace('.mp3', suffix)
    path_summary = os.path.join(PATH_SUMMARY_FILES, file_summary)

    return path_summary


def getSpeakerSummaryPath(speaker, suffix):

    file_summary = 'speaker.' + speaker + suffix
    path_summary = os.path.join(PATH_SUMMARY_FILES, file_summary)

    return path_summary


def getSeriesSummaryPath(series, suffix):

    file_summary = 'series.' + series + suffix
    path_summary = os.path.join(PATH_SUMMARY_FILES, file_summary)

    return path_summary


def getBiographyText(speaker):

    path_biography = os.path.join(PATH_BIOGRAPHY_FILES, speaker) + '.txt'
    if not os.path.exists(path_biography): return ''

    with open(path_biography) as fd:
        biography_text = fd.read()
    return biography_text


def writeJSONData(path_json, name, summary, list_elements):

    print(f'Writing:  {path_json}')
    data = {}
    with open(path_json, "w") as fd:
        data['title'] = name
        data['list_elements'] = list_elements
        if summary: data['summary'] = summary
        json.dump(data, fd, indent=4)


def writeTextData(path_text, text):

    with open(path_text, "w") as fd:
        print(f'writing text: {path_text}')
        fd.write(text)



def textToInteger(text):

    hashed = hashlib.sha256(text.lower().encode())
    value =  int.from_bytes(hashed.digest()[:8], 'big')

    return(abs(value))



def remove_prefix_from_text(text, prefix):

    if text.strip().startswith(prefix):
        new_text = text[len(prefix):].strip()
        new_text = new_text[0].capitalize() + new_text[1:]
        return new_text
    else:
        return text


def filter_common_words(input_str):

    words = input_str.split()
    filtered_words = [word for word in words if word.lower() not in FILTER_WORDS]
    output_str = ' '.join(filtered_words)

    return output_str


def remove_punctuation(s):

    return ''.join([char for char in s if char not in string.punctuation])


def remove_last_punctuation(s):
    if s and s[-1] in string.punctuation:
        return s[:-1]
    return s


def collectionExists(name_collection):

    try:
        collection_info = VectorDB.get_collection(collection_name=VECTOR_COLLECTION_AD_KEYS)
    except:
        return False

    return True


def loadRankedTalksDict():

    with open(PATH_RANKED_TALKS, 'r') as fd:
        list_ranked_talks = json.load(fd)

    dict_ranked_talks  = {talk["url"]: talk for talk in list_ranked_talks}
    return dict_ranked_talks


def loadRuleActions():

    with open(PATH_RULE_ACTIONS, 'r') as fd:
        list_rule_actions = json.load(fd)

    dict_rule_actions = {rule["trigger"].lower(): {"action": rule["action"], "parameter": rule["parameter"]} for rule in list_rule_actions}

    return dict_rule_actions


# check to see if PORT is available for binding
# used to prevent multiple instances competing for port
def is_port_available(host, port):

    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((host, port))
        serverSocket.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False



#
# Main
#
logging.basicConfig(filename=PATH_AUDIODHARMA_LOG,  level=logging.INFO, format='%(asctime)s - %(message)s')
DictRankedTalks = loadRankedTalksDict()
DictRuleActions = loadRuleActions()


