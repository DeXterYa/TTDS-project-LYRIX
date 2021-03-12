import numpy as np

from unidecode import unidecode

# Inputs:
#   query        - string query.
#   preprocessor - instance of Preprocessor class from src.preprocessor.
#   song_col     - MongoDB collection object that holds the actual songs with all the data.
#   index_col    - MongoDB collection object that holds the index
#   top_k        - number of songs that you want to output.
# Output:
#   songs - list of top_k song objects most relevant to the query.
def ranked_search(query, preprocessor, songs_col, index_col, top_k):

    # Remove nonenglish characters.
    query = unidecode(query)

    # Preprocess the query with all stemmers available in NLTK.
    query  = preprocessor.preprocess(query, of_type='query')
    query  = query.split()
    scores = dict()
    
    # For each term find songs that contain it.
    for term in query:
        records = []
        
        # Query the index in mongodb to get songs that contain the word.
        for record in index_col.find({'t': term}):
            records += record['p']
            
        # The term does not occur in any song.
        if len(records) == 0:
            continue
        
        for song_id, score in records:
            
            if song_id not in scores:
                scores[song_id] = 0
                
            # scores dict maps song_id to its BM25 score for the query.
            scores[song_id] = scores[song_id] + score
    
    # Sort the songs by the BM25 score with respect to the query in descending order. Then select
    # select just top_k best songs.
    idx     = list(np.argsort(list(scores.values())))[::-1]
    results = list(np.array(list(scores.keys()))[idx])[:top_k]
    songs   = []
    relevance = []

    for song_id in results:

        # Query the songs collection in mongodb to load the actual song.
        for song in songs_col.find({'_id': int(song_id)}):
            songs += [song]
            relevance += ["{:.2f}".format(scores[song_id])]
    
    return songs, relevance