# Audiodharma.ai


An instance of this code runs on www.audiodharma.ai.
<p>
AudioDharma AI is an integration of thousands of Buddhist talks with Artificial Intelligence. These talks were given at the Insight Meditation Center (IMC) in Redwood City, California, and can be found at www.audiodharma.org. They include hundreds of diverse speakers with various viewpoints, in talks given over a period of many years..
<p>
With IMC's permission, an AI has been trained to be a guide to these talks. Her name is Sophia, and she acts as a guide to the underlying material.
<p>

Although tailored specifically to that use-case, this project could also serve as a template for any effort which wants to bolt AI onto an existing large corpus of data.


# Prerequisites

Python3
<br>
Qdrant vector database, running in a docker container
<br>
OpenAI 3.5 Keys and API  (portable to any LLM with similar functionality)
<p>
The base installation runs on Ubuntu 20.04 and Apache.


# Overview

All the javascript code can be found in ./common/main.js.  This integrates with the HTML files, and provides all the site interactivity.
<p>
Main.js interacts with the API implemented in the sophia process found in ./bin/sophia.py. Sophia runs as a webserver on port SOPHIA_SERVER_PORT. 
<p>
The vector database is used for searching and generating similarity data for talks and speakers.
It runs on port QDRANT_SERVER_PORT. Sophia.py and various supporting tools interact with the database via that port.
<p>
All globals and common utilities are found in ./bin/common.py.
<p>
All other supporting runtime code is found in ./bin
<p>
All data files are found in ./data.  A snapshot of the file structure and data can be downloaded here:  
 <a href="https://www.audiodharma.ai/archives/snapshot_data.zip" download>Download</a>
<P>
Note that this zip excludes the underlying mp3 files.  
If required, these can be obtained from www.audiodharma.org.

# Building

To build all required data files and populate the vector database, execute ./bin/xbuild.  This does the following:
- translates all raw talk transcripts into a simple standard HTML format
- summaries these talks
- creates metadata json files for these talks, and quick-lookup indexes
- creates metadata json files for all speakers
- using qdrant, vectorizes all talks and speakers
- using the vectors in qdrant, creates similarity files for all talks and speakers
- creates metadata json files for all talk series
<p>
All of the generated json files are stored in respective directories in ./data. The sophia.py process then refers to these directories to satisfy API calls.











