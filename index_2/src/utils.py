import json

from math    import ceil
from tqdm    import trange
from glob    import glob
from pathlib import Path

# Splits dataset to number of smaller sets. Large files are hard to fit in RAM so working on smaller
# files is suggested. Optimally, 200,000 songs in file for 16 GB RAM. If you have less RAM use 
# smaller split. (Use 100,000 songs to fit 1 GB RAM in our server.)
# Inputs:
#   file_name       - name of large file that you want to split.
#   songs_per_split - number of songs that you want to have in single split.
def split_dataset(file_name, songs_per_split=200000):

    # Load the big dataset.
    with open(file_name, 'r') as file:
        dataset = json.loads([line for line in file][0])

        file.close()

    dataset = standardize_dataset(dataset)

    # Compute number of output partitions.
    num_splits = int(ceil(len(dataset) / songs_per_split))

    Path('./inputs').mkdir(exist_ok=True)

    for split in trange(num_splits, desc='Splitting datset'):
        small_dataset = dataset[split*songs_per_split:(split+1)*songs_per_split]

        with open('./inputs/raw_' + str(split) + '.json', 'w') as file:
            json.dump(small_dataset, file)
            file.close()

# MongoDB does not accept JSON files that have dot '.' character in the field name. This function
# removes such dots from any field names in the credits dictionary of any song.
def standardize_dataset(dataset):
    for song in dataset:
        for label, value in list(song['credits'].items()):
            if '.' in label:

                # Remove dot entirely - replace it by empty string.
                new_label                  = label.replace('.', '')
                song['credits'][new_label] = value
                
                del song['credits'][label]

    return dataset

# Converts dictionary song representation to one string. Such string contains the following field 
# values:
#   - title
#   - lyrics
#   - album
#   - author name (without link)
#   - tags
#   - all credit dictionary field values (without links)
def song_to_string(song):
    song_txt = []

    for meta_data in ['title', 'lyrics', 'album']:
        song_txt += [song[meta_data]]

    song_txt += [song['author'][0]]
    song_txt += song['tags']

    for credit_vals in song['credits'].values():
        for credit_val in credit_vals:
            song_txt += [credit_val[0]]
        
    song_txt = ' '.join(song_txt)

    return song_txt

# Collection is MongoDB collection object instance into which you want to insert the data. You can
# insert either song or index data. Use of_type string argument to specify whether you want
# to insert songs or index. The songs data will be take from all files named 'raw_<number>.json'
# from inputs directory. The index data will be take from all files named 'index_<number>.json'
# from indexes directory.
def insert_data_to_mongo(collection, of_type):
    assert of_type in ['songs', 'index'], 'of_type must be either songs or index.'

    if of_type == 'songs':
        file_list = glob('./inputs/raw_*.json')
    elif of_type == 'index':
        file_list = glob('./indexes/index_*.json')

    N = len(file_list)

    for idx in trange(N):
        file_name = file_list[idx]

        with open(file_name, 'r') as file:
            data = json.loads([line for line in file][0])

            file.close()

        collection.insert_many(data)

    # Create B-tree
    if of_type == 'index':
        collection.create_index('t', name='term')