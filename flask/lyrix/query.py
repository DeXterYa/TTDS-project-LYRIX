import numpy as np
import string
from unidecode import unidecode

# Inputs:
#   query        - string query.
#   preprocessor - instance of Preprocessor class from src.preprocessor.
#   song_col     - MongoDB collection object that holds the actual songs with all the data.
#   index_col    - MongoDB collection object that holds the index
#   top_k        - number of songs that you want to output.
# Output:
#   songs - list of top_k song objects most relevant to the query.
def ranked_search(query, preprocessor, songs_col, index_col, artist_col, date_col, is_advanced, advaned_dict, lang='en'):

    # Remove nonenglish characters.
    query = unidecode(query)

    # Preprocess the query with all stemmers available in NLTK.
    query  = preprocessor.preprocess(query, of_type='query', lang=lang)
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
    songs   = []
    relevance = []
    


    if (not is_advanced):
        
        results = list(np.array(list(scores.keys()))[idx])
        
       
    else:
        
        results = set(scores.keys())
        
        singer = advaned_dict["singer"]
        
        if singer is not None and len(singer.strip())!=0:
            translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
            name_list = singer.lower().translate(translator).split()
            

            for record in artist_col.find({"_id": {"$in":name_list}}):
                
                results = results.intersection(set(record['indexes']))

            


        
        startdate = advaned_dict["startdate"]
        enddate = advaned_dict["enddate"]
        

        if bool(startdate) or bool(enddate): 
            song_ids_with_date = []
            if bool(startdate) and bool(enddate):
                for record in date_col.find({"_id": {"$gt": int(startdate)-1, "$lt": int(enddate)+1}}):
                    song_ids_with_date += list(record['indexes'])
                results = results.intersection(set(song_ids_with_date))

            elif bool(startdate):
                for record in date_col.find({"_id": {"$gt": int(startdate)-1}}):
                    song_ids_with_date += list(record['indexes'])
                results = results.intersection(set(song_ids_with_date))
                
            elif bool(enddate):
                for record in date_col.find({"_id": {"$lt": int(enddate)+1}}):
                    song_ids_with_date += list(record['indexes'])
                results = results.intersection(set(song_ids_with_date))

        results = sorted(list(results), key=lambda x: scores[x], reverse=True)
        
        

    
    return results, scores, len(results)