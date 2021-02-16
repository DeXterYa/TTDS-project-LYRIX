import json

from math    import ceil
from tqdm    import trange
from pathlib import Path

# Splits dataset to number of smaller sets. Large files are hard to fit in RAM so working on smaller
# files is suggested. Optimally, 200,000 songs in file for 16 GB RAM. If you have less RAM use 
# smaller split.
# Inputs:
#   file_name       - name of large file that you want to split.
#   songs_per_split - number of songs that you want to have in single split.
def split_dataset(file_name, songs_per_split=200000):

    # Load the big dataset.
    with open(file_name, 'r') as file:
        dataset = json.loads([line for line in file][0])

        file.close()

    # Compute number of output partitions.
    num_splits = int(ceil(len(dataset) / songs_per_split))

    Path('./inputs').mkdir(exist_ok=True)

    for split in trange(num_splits, desc='Splitting datset'):
        small_dataset = dataset[split*songs_per_split:(split+1)*songs_per_split]

        with open('./inputs/raw_' + str(split) + '.json', 'w') as file:
            json.dump(small_dataset, file)
            file.close()

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
