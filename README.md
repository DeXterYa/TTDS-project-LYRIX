
# How do I access the dataset?
### [Dataset access](https://drive.google.com/drive/folders/1mAWpsMSa8yV_wQ3U1l8dK9FtwvLOc7NA?usp=sharing)


__Notes:__
+ There are two directories **_inputs_** and **_indexes_**.
+ **_inputs_** directory contains **_37_** `raw_<file_id>.json` files. Each file contains a list of song objects that we have scraped from Genius. Each file contains at most 50,000 songs. This number of songs was chosen so that loading such a file in Python does not take more than **_400 MB of RAM_**. Together the 37 files compose our overall dataset of **_1,809,543_** songs.
+ The song objects already have a `_id` field used as ID by MongoDB.
+ **_indexes_** directory contains **_128_** `index_<file_id>.json` files. Each file contains a list of inverted index objects for separate terms. Our overall index was split into 128 chunks so that loading any index file into Python memory does not take more than **_500 MB of RAM_**.

__Format of inverted index object for a specific term:__ 
```
{'t': 'tellepath',
 'p': [[334794, 1.5978419346570618],
       [143979, 1.5329157162473461],
       [282062, 1.1846364784661536]]}
```
+ `'t'` field stands for term name.
+ `'p'` field stands postings. It is a list of tuples. The first term in each tuple is a song ID. The second element of the tuple is a float which indicates the **_BM25 score_** associated with the term in the song with a specified ID. The postings list is sorted in the descending order of the BM25 scores.

# I have a ready dataset and index, how do I use it?
### Project structure
Before using any code from this repo ensure that your project has the following structure, with all of the directories. Much of the code in this repo assumes the following project structure and it may not work correctly without it.
```
index_2
├── indexes
├── inputs
├── lexicon_splits
├── preprocessed
├── src
│   ├── index.py
│   ├── preprocessor.py
|   ├── query.py
│   ├── utils.py
│   └── workers.py
└── runner.py
```
### Load songs into MongoDB
Steps to take:
1. Ensure that you are in the index2 directory. (`cd index2`)
2. Place the files in which you store the songs into `index2/inputs`. All of the files should have `raw_<file_id>.json` name.
3. Run the following code:
```
import pymongo

from src.utils import insert_data_to_mongo

client     = pymongo.MongoClient("mongodb://localhost:27017/")
database   = client["lyrix"]
collection = database["songs"]

insert_data_to_mongo(collection, of_type='songs')
```
The above code is going to load every `raw_<file_id>.json` from the `index2/inputs` directory into Python memory (one at a time). The collection located in the `raw_<file_id>.json` is then inserted into the MongoDB.
### Load index into MongoDB
Steps to take:
1. Ensure that you are in the index2 directory. (`cd index2`)
2. Place the files in which you store the index into `index2/indexes`. All of the files should have `index_<file_id>.json` name.
3. Run the following code:
```
import pymongo

from src.utils import insert_data_to_mongo

client     = pymongo.MongoClient("mongodb://localhost:27017/")
database   = client["lyrix"]
collection = database["song_index"]

insert_data_to_mongo(collection, of_type='index')
```
The above code is going to load every `index_<file_id>.json` from the `indexes` directory into Python memory (one at a time). The collection located in the `index_<file_id>.json` is then inserted into the MongoDB. When all of the files are inserted into the MongoDB a **_B-Tree_** is created on the `'t'` field of the index objects by the MongoDB.
### Time to Query!!!
```
import pymongo

from src.preprocessor import Preprocessor
from src.query        import ranked_search

client           = pymongo.MongoClient("mongodb://localhost:27017/")
database         = client["lyrix"]
songs_collection = database["songs"]
index_collection = database["song_index"]

query        = 'Some example song lyrics'
preprocessor = Preprocessor()
top_k        = 20

relevant_songs = ranked_search(query, preprocessor, songs_collection, index_collection, top_k)
```