#!/usr/bin/python
#
# Create json files for every series
#
import os
import sys
import json
import re
from common import  LOG, getAllTalks, getTalkSummaryPath, getSeriesPath, getAllSeries, getSeriesSummaryPath, getIndexPath, writeJSONData

#
# Main
#
print('genseries starts')

list_series = []
for series, list_talks in getAllSeries():

    if len(series) < 5: continue
    if len(list_talks) == 0: continue
    series = series.replace('/', '.')

    #series = "test"
    path_series = getSeriesPath(series)
    path_summary_long = getSeriesSummaryPath(series, '.long')
    path_summary_short = getSeriesSummaryPath(series, '.short')

    summary_short = summary_long = 'Not Available'
    if not os.path.exists(path_summary_long): continue
    if not os.path.exists(path_summary_short): continue
    with open(path_summary_long, 'r') as fd:
        summary_long = fd.read()
    with open(path_summary_short, 'r') as fd:
        summary_short = fd.read()

    with open(path_series, 'w') as fd:

        # output series file
        data = {}
        data['title'] = series
        data['date'] = list_talks[0]['date']
        data['summary_short'] = summary_short
        data['summary_long'] = summary_long
        data['list_elements'] = list_talks
        data['count_talks'] = len(list_talks)
        json.dump(data, fd, indent=4)

        # add talk data to index series
        data_index = {}
        data_index['title'] = series
        data_index['date'] = list_talks[0]['date']
        data_index['summary_short'] = summary_short
        data_index['summary_long'] = summary_long
        data_index['count_talks'] = len(list_talks)
        list_series.append(data_index)

# generate a json file indexing all series
data_index = {}
list_series_sorted_name = sorted(list_series, key=lambda x: x['title'])
list_series_sorted_date = sorted(list_series, key=lambda x: x['date'])
list_series_sorted_date.reverse()
data_index['sorted_alphabetically'] = list_series_sorted_name
data_index['sorted_by_talk_date'] = list_series_sorted_date

path_index_series = getIndexPath('series', '')
writeJSONData(path_index_series, 'Series', '', data_index)

LOG('genseries completes')
total_series = len(list_series)
LOG(f'total series generated: {total_series}')


