# INDEX
## How to use
```
from index import SearchEngine
```
### Build new index
```
se = SearchEngine(fileName='all_songs.json', indexReady=False)
```
Inputs:
* `fileName` - `.json` file with collection of songs scraped from Genius. The file should be a dictionary that maps a song ID to the corresponding song object *(dictionary)*

Outputs:
* `index.txt` - as in coursework, but positions of words in the text were replaced by simple term frequency since we are doing a ranked search.

### Load Ready index
```
se = SearchEngine(fileName='index.txt', indexReady=True)
```
Input:
* `fileName` - `.txt` file similar to `index.txt` from coursework. *(but term frequencies instead of positions in text )*
### Answer single string query
```
documentIDs = se.rankedSearch(query_string)
```
Outputs:
* `documentIDs` - sorted list of most relevant documents for a query. *(descending order)*