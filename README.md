# INDEX
### Things to note
* We are not storing the positions of terms in the text. We are doing a ranked search with TFIDF, so we do not need positions of terms.
* In the original genius-scraped dataset that I posted the songs had no ID. To fix this in https://drive.google.com/drive/folders/1mAWpsMSa8yV_wQ3U1l8dK9FtwvLOc7NA there is a new file called `all_songs_0.json` which stores a dictionary in which a song ID is mapped to the song object. If you want to work with the ready `genius_index.json` from https://drive.google.com/drive/folders/1mAWpsMSa8yV_wQ3U1l8dK9FtwvLOc7NA you need to follow the song IDs from `all_songs_0.json`. If you want to use different IDs you need to build a new index which takes about 3 hours.
* Currently the index was built on the lyrics field of a song only. Later we will have to change the `index.py` code to allow for search among song's metadata also.

## How to use
```
from index import SearchEngine
```
### Build new index
```
se = SearchEngine()

se.buildIndex(inFile='all_songs.json', outFile='index.json')
```
Inputs:
* `inFile` - `.json` file with collection of songs scraped from Genius. The file should be a dictionary that maps a song ID to the corresponding song object *(dictionary)*
* `outFile` - the name of the `.json` file in which the index will be saved.

Outputs:
* `outFile` - File in which the index is saved as a JSON object. An object is a dictionary that maps each term to its postings. The posting is a dictionary that maps a document ID to the number of times the term occurs in that document. **SPECIAL MAPPING** - `DOCUMENT_COUNT` key in the main dictionary stores the total number of songs in the collection. *(needed for TFIDF computation)* 

### Load Ready index
```
se = SearchEngine()

se.loadIndex(fileName='index.json')
```
Input:
* `fileName` - `.json` file, format as in output of `buildIndex`.
### Answer single-string query
```
documentIDs = se.rankedSearch(query_string)
```
Outputs:
* `documentIDs` - sorted list of most relevant documents for a query. *(descending order)*
