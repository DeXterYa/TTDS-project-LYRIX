# Table of contents:
- [How do I access the dataset?](#how-do-i-access-the-dataset)
- [I have a ready dataset and index, how do I use them?](#i-have-a-ready-dataset-and-index-how-do-i-use-them)
  * [Project structure](#project-structure)
  * [Load songs into MongoDB](#load-songs-into-mongodb)
  * [Load index into MongoDB](#load-index-into-mongodb)
  * [Time to Query!!!](#time-to-query)
	  * [Searching algorithm](#Searching-algorithm)
- [Index building](#index-building)
	- [The easy way](#the-easy-way)
	- [The hard way _(manual)_](#the-hard-way-manual)
		- [Split the dataset](#split-the-dataset)
		- [Preprocessing](#preprocessing)
		- [Convert raw _term frequencies_ to _BM25 TF-components_](#convert-raw-term-frequencies-to-bm25-tf-components)
		- [Compute and partition the lexicon](#compute-and-partition-the-lexicon)
		- [Build index](#build-index)
		- [Compute full _BM25 scores (with IDF-components)_](#compute-full-bm25-scores-with-idf-components)
- [Problems](#problems)
- [Extensions](#extensions)
# How do I access the dataset?
### [Dataset access](https://drive.google.com/drive/folders/1mAWpsMSa8yV_wQ3U1l8dK9FtwvLOc7NA?usp=sharing)


#### Notes
+ There are two directories **_inputs_** and **_indexes_**.
+ **_inputs_** directory contains **_37_** `raw_<file_id>.json` files. Each file contains a list of song objects that we have scraped from Genius. Each file contains at most 50,000 songs. This number of songs was chosen so that loading such a file in Python does not take more than **_400 MB of RAM_**. Together the 37 files compose our overall dataset of **_1,809,543_** songs.
+ The song objects already have a `_id` field used as ID by MongoDB.
+ **_indexes_** directory contains **_128_** `index_<file_id>.json` files. Each file contains a list of inverted index objects for separate terms. Our overall index was split into 128 chunks so that loading any index file into Python memory does not take more than **_500 MB of RAM_**.

#### Format of inverted index object for a specific term
```
{'t': 'tellepath',
 'p': [[334794, 1.5978419346570618],
       [143979, 1.5329157162473461],
       [282062, 1.1846364784661536]]}
```
+ `'t'` field stands for term name.
+ `'p'` field stands postings. It is a list of tuples. The first term in each tuple is a song ID. The second element of the tuple is a float which indicates the **_BM25 score_** associated with the term in the song with a specified ID. The postings list is sorted in the descending order of the BM25 scores.

# I have a ready dataset and index, how do I use them?
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
The above code is going to load every `raw_<file_id>.json` from the `index2/inputs` directory into Python memory _(one at a time)_. The collection located in the `raw_<file_id>.json` is then inserted into the MongoDB.
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
The above code is going to load every `index_<file_id>.json` from the `indexes` directory into Python memory _(one at a time)_. The collection located in the `index_<file_id>.json` is then inserted into the MongoDB. When all of the files are inserted into the MongoDB a **_B-Tree_** is created on the `'t'` field of the index objects by the MongoDB.
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
+ `query` is a simple string query that you are looking for.
+ `relevant_songs` is the list of song objects in descending order of their BM25 scores associated with the query.
+ `top_k` is an integer that specifies the length of the returned `relevant_songs` list. _(The larger it is the longer the querying takes, as more records must be retrieved from the database)_


#### Searching algorithm
+ Use unidecode to remove _"weird"_ characters. The same mapping was done on the songs. Examples: convert 
	+ _ł_ to _l_
	+  _ą_ to _a_
	+  _ę_ to _e_
	+ _ż_ to _z_
+ Case fold the query.
+ If there is a sequence of characters that has non-alphanumerics, no spaces within, but starts and ends with spaces, we add such sequence of characters without non-alphanumerics to the end of the query. Examples:
	+ i'm to im
	+ 34+45 to 3435
	+ ph.d. to phd
	+ g.o.a.t. to goat
	+ (0131)-xxx-aaaa to 0131xxxaaaa
+ Replace all nonalphanumeric characters by spaces. *(maintain numbers)* Examples:
	+ i'm to i m
	+ 34+45 to 34 35
	+ ph.d. to ph d
	+ g.o.a.t. to g o a t
	+ (0131)-xxx-aaaa to 0131 xxx aaaa
+ **_Result of the previous two operataions_**: user can type GOAT or G.O.A.T. and he is going to find songs that have G.O.A.T. word in the lyrics. _(Same preprocessing was undertaken on the songs)_
+ Now the query is a sequence of terms. Stem each term in the query with every **_NLTK Snowball language stemmer_** that is available. _(except for Arabic and Russian cause we do not have any Arabic or Russian songs in the collection. Thus, our list of supported languages includes Danish, Dutch, English, Finnish, French, German, Hungarian, Italian, Norwegian, Portuguese, Romanian, Spanish, and Swedish)_ We add each newly obtained stem form of a word to a **_set_** of all stem forms obtained for all terms in the query. Now use the inverted index to query each term from the set. 
+ The frequency of terms in the query is not taken into account. Particular term either is or is not in the query. _(That's why I have highlighted the word **set** )_
+ In the inverted index, we store the precomputed **_BM25 scores_** for all term-document pairs. We can easily retrieve the indexes for the terms in the query and sum the weights for all terms in all documents, then sort the documents by their cumulative scores and return only the most relevant ones.

# Index building
### The easy way
The full pipeline of building the index out of a huge dataset file is contained within the `runner.py` file. As the name of this file suggests it can be used to run the index building process from the beginning to the end. I have attempted to shorten the index building process with multiprocessing, however, it was not a good idea as RAM constraints are the most crucial when dealing with such a huge file. The whole process takes several hours, so I suggest running it overnight.

Example of running:
```
python runner.py --dataset path/to/dataset/json/file --split 50000 --num_processes 16 --num_indexes 128
```
#### Commandline inputs:
+ `--dataset` - path to a JSON file that holds the entire dataset with all songs. The songs should be stored in a list of objects, where each object represents one song.
+ `--split` - The huge dataset with all the songs will be split into several smaller files to prevent RAM overflow. This parameter specifies how many songs each such smaller split should have. I suggest using something between 50,000 and 200,000. The larger the value of this parameter the faster the index building is, but the more likely it is that you will overflow the RAM.
+ `--num-processes` - Number of concurrent processes that you want to use when preprocessing the song collection. Other parts of the index building process are sequential due to high RAM requirements.
+ `--num_indexes` - Number of files in which the overall inverted index will be stored. `--num_indexes 128` means that the index will be stored in 128 JSON files. The larger this value is the longer the process takes, but the less RAM it requires. For fast index building I suggest using a very small value of this parameter _(8 for example)_, but not too small to prevent RAM overflow and costly back-and-forth disk accesses. _(When the index was ready I have further split the 8 index files into 128 ones manually)_ The optimal value of this parameter also depends on the value of the `--split` parameter. I suggest using something like `--split 100000 --num_indexes 8` when you have 16 GB RAM. If you have less RAM use smaller `--split` and more `--num_indexes`.
#### Outputs:
+ `./index2/inputs/raw_<file_id>.json` - Set of files into which the original huge dataset was split. Each file contains at most `--split` song objects.
+ `./index2/preprocessed/ready_<file_id>.json` - Set of files that contain the song after preprocessing, in a inverted index format. So each song is dictionary that maps a term into a tuple where first element is the song id and the second one is the TF-component of the BM25 score.
+ `./index2/lexicon_splits/split_<file_id>.json` - Set of `--num-indexes` files. Each file contains a part of the overall collection lexicon. `index_n.json` contains the inverted index for terms in `split_n.json`
+ `./index2/indexes/index_<file_id>.json` - Set of `--num-indexes` files that together compose the overall inverted index for the collection.

**WARNING: The total size of the song collection is currently hardcoded. _(1,809,543)_ If you want to use a different dataset you have to change this value manually in the code. _(Line 36 in `runner.py`)_**

### The hard way _(manual)_
#### Split the dataset
```
from src.utils import split_dataset

dataset = 'c:/path/to/your/dataset/json/file'
split   = 50000

split_dataset(dataset, split)
```
#### Preprocessing
```
from src.workers import preprocess_collection

num_processes = 16

if  __name__ == '__main__':
	mp.freeze_support()
	preprocess_collection(num_processes)
```
#### Convert raw _term frequencies_ to _BM25 TF-components_
```
from src.index import compute_bm25_tfs

compute_bm25_tfs()
```
#### Compute and partition the lexicon
```
from src.index import partition_lexicon

num_index_files = 8

partition_lexicon(num_index_files)
```

#### Build index
```
from src.index import build_index

num_index_files = 8

build_index(num_index_files)
```

#### Compute full _BM25 scores (with IDF-components)_
```
from src.index import compute_bm25_idfs

collections_size = 1809543

compute_bm25_idfs(collection_size)
```

# Problems

# Extensions