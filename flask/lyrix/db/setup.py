import pandas as pd
import json
import pymongo


def insert_dataset_into_db(dataset_path='../../../../index/dataset.json', db_name='lyrix', collection_name='genius'):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client[db_name]
    lyrics_collection = database[collection_name]

    # assume dataset is in json format    
    with open(dataset_path) as dataset_file:
        dataset = json.load(dataset_file)

    # relevant fields to be stored in db
    relevant_fields = ['url', 'title', 'author', 'lyrics', 'language', 'image_url', 'album', 'video_url', 'tags', 'id']

    for doc_id in dataset.keys():
        lyrics_collection.insert_one({key:dataset[doc_id][key] for key in relevant_fields})


insert_dataset_into_db()