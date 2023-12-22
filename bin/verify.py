#!/usr/bin/python
# 
# sophia.py
#
# implements all APIs to access system
# runs as http server on port SOPHIA_SERVER_PORT
#
import os
import sys
from common import getTalkSummaryPath, getAllTalks


print('verification begins')
for talk in getAllTalks():
    #print(talk['title'])
    if talk['ln'] != 'en': continue

    path_summary_key = getTalkSummaryPath(talk, '.key')
    path_summary_short = getTalkSummaryPath(talk, '.short')
    path_summary_long = getTalkSummaryPath(talk, '.long')

    if not os.path.exists(path_summary_key):
        print(f'Error: Missing {path_summary_key}')
        continue
    if os.path.getsize(path_summary_key) < 10:
        print(f'Error: Truncated {path_summary_key}')

print('verification ends')

