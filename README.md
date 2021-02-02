# INDEX
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
