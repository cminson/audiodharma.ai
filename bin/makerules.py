#!/usr/bin/python
#
#
import os
import sys
import json
from common import  getAllSpeakers


#
# Main
#

list_rules = []
print('test starts')



list_speaker_permute = ['X talks', 'talks X', 'X all', 'X all talks', 'talks by X', 'all talks by X', 'talks X', 'every talk by X', 'all talks by X', 'every talk X', 'show every talk X', 'show every talk by X', 'display every talk X', 'display every talk by X', 'give me every talk by X', 'talks X', 'talk X', 'show all talks by X', 'show me all talks by X', 'display talks by X', 'display all talks by X', 'give me all talks by X', 'display all talks by X', 'all X talks', 'show me talks by X', 'display talks by X', 'all talks X', 'show X talks', 'display X talks', 'show talks X', 'display talks X', 'show me X talks', 'display X talks']

list_all_permute = ['recent', 'recent talks', 'all recent talks', 'every recent talk', 'current', 'current talks', 'all current talks', 'all talks', 'new talks', 'new', 'talks', 'every talk', 'every recent talk', 'display talks', 'display all talks', 'display new talks', 'display current talks', 'show talks', 'show all talks', 'show recent talks', 'show new talks', 'show every talk', 'display every talk']

def make_speaker_event(trigger):

    trigger = trigger.lower()
    event = {}
    event['trigger'] = trigger
    event['action'] = 'SPEAKER_TALKS'
    event['parameter'] = speaker
    list_rules.append(event)

    for permute in list_speaker_permute:
        ptrigger = permute.replace('X', trigger)
        event = {}
        event['trigger'] = ptrigger
        event['action'] = 'SPEAKER_TALKS'
        event['parameter'] = speaker
        list_rules.append(event)

    trigger = trigger.lower() + 's'
    event = {}
    event['trigger'] = trigger
    print("XX", trigger)
    event['action'] = 'SPEAKER_TALKS'
    event['parameter'] = speaker
    list_rules.append(event)

    for permute in list_speaker_permute:
        ptrigger = permute.replace('X', trigger)
        event = {}
        event['trigger'] = ptrigger 
        event['action'] = 'SPEAKER_TALKS'
        event['parameter'] = speaker
        list_rules.append(event)


def make_all_event(trigger):

    trigger = trigger.lower()
    event = {}
    event['trigger'] = trigger
    event['action'] = 'ALL_TALKS'
    event['parameter'] = ''
    list_rules.append(event)


for trigger in list_all_permute:
    make_all_event(trigger)



for speaker, _ in getAllSpeakers():

    print(speaker)

    make_speaker_event(speaker)

    list_names = speaker.split()
    if len(list_names) == 3:
        make_speaker_event(list_names[0])
        make_speaker_event(list_names[2])

    if len(list_names) == 2:
        make_speaker_event(list_names[0])
        make_speaker_event(list_names[1])

    if len(list_names) == 1:
        make_speaker_event(list_names[0])



with open('../config/RULES.JSON', 'w') as fd:

    json.dump(list_rules, fd, indent=4)




