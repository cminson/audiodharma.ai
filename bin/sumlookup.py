#!/usr/bin/python
#
# Author: Christopher Minson
#
# Look up summary files give an .mp3
#
import os
import datetime
import sys
from common import PATH_SUMMARY_FILES


if len(sys.argv) > 1:
    file_mp3 = sys.argv[1]
    file_summary = 'talk.' + file_mp3.replace('.mp3', '.key')
    path_summary_key = os.path.join(PATH_SUMMARY_FILES, file_summary)
    if not os.path.exists(path_summary_key):
        print(f'Does not exist: {path_summary_key}')
        exit()
    print('-----------\n')
    with open(path_summary_key) as fd:
        text = fd.read()
        print(f'KEY TEXT:  {text}')
    print('\n')

    file_summary = 'talk.' + file_mp3.replace('.mp3', '.brief')
    path_summary_key = os.path.join(PATH_SUMMARY_FILES, file_summary)
    with open(path_summary_key) as fd:
        text = fd.read()
        print(f'BRIEF TEXT: {text}')
    print('\n')

    file_summary = 'talk.' + file_mp3.replace('.mp3', '.long')
    path_summary_key = os.path.join(PATH_SUMMARY_FILES, file_summary)
    with open(path_summary_key) as fd:
        text = fd.read()
        print(f'LONG TEXT: {text}')

else:
    print('No query')



