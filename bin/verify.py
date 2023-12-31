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
errors = 0
for talk in getAllTalks():
    #print(talk['title'])
    if talk['ln'] != 'en': continue

    path_summary_key = getTalkSummaryPath(talk, '.key')
    path_summary_short = getTalkSummaryPath(talk, '.short')
    path_summary_long = getTalkSummaryPath(talk, '.long')

    if not os.path.exists(path_summary_key):
        print(f'Error: Missing {path_summary_key}')
        errors += 1
        continue
    if os.path.getsize(path_summary_key) < 10:
        print(f'Error: Truncated {path_summary_key}')
        errors += 1
        continue

    if os.path.getsize(path_summary_short) < 100:
        print(f'rm {path_summary_short}')
        errors += 1
        continue

    #if not os.path.exists(path_summary_long): continue
    if os.path.getsize(path_summary_long) < 200:
        print(f'rm {path_summary_long}')
        errors += 1
        continue

print(f'errors:  {errors}')
print('verification ends')

