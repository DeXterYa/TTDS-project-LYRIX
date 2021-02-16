import json
import os
import multiprocessing as mp

from glob             import glob
from tqdm             import trange, tqdm
from math             import ceil
from collections      import Counter
from src.preprocessor import Preprocessor
from src.utils        import song_to_string

# Divides equally set of songs among processes. Returns process_songs - list of lists. Each list
# in process_songs includes songs that the process with corresponding index should preprocess.
def divide_work(songs, num_processes):
    interval      = int(ceil(len(songs) / num_processes))
    process_songs = []
    
    for process in range(num_processes):
        process_songs += [songs[process*interval:(process+1)*interval]]

    return process_songs

# Preprocesses list of songs. Converts song dictionary representation into its inverted index.
# Returns list of such inverted indexes. Inverted index is a dictionary which maps a word to a tuple
# in which first element is song ID (int, as _id field in MongoDB), seconde element is the frequency
# of that word.
def worker(process_num, songs):
    preprocessed = []
    preprocessor = Preprocessor()
    tqdmText     = 'process ' + '{}'.format(process_num).zfill(2)

    # Progress bar for process.
    with tqdm(total=len(songs), desc=tqdmText, position=process_num+1) as pbar:

        for song in songs:

            # Neglects languages we do not support.
            if song['language'] in preprocessor.stemmers:

                # Convert dictionary song representation into a string.
                txt = song_to_string(song)
                txt = preprocessor.preprocess(txt, of_type='song', lang=song['language']).split()

                # Convert song into BOW representation.
                bow      = Counter(txt)
                inverted = dict()

                # Converted BOW song representation into inverted index.
                for word, freq in bow.items():
                    inverted[word] = (int(song['_id']), freq)

                preprocessed += [inverted]

            # Update progress bar.
            pbar.update(1)

    return preprocessed

# Preprocesses all songs. The songs should be in inputs folder in JSON files. The JSON file should
# hold a list of songs, where song is represented as a dictionary. Output: set of read_<id>.json
# files in the preprocessed directory where each file holds each song in inverted index format.
def preprocess_collection(num_workers):
    file_list = glob('./inputs/*.json')
    file_num  = len(file_list)

    for col_idx in trange(file_num, desc='Preprocessing total'):
        collection = file_list[col_idx]

        # Load subset of dataset.
        with open(collection, 'r') as file:
            songs = json.loads([line for line in file][0])

            file.close()

        # Assign equal number of songs for preprocessing to each process.
        process_songs = divide_work(songs, num_workers)

        pool        = mp.Pool(processes=num_workers, initargs=(mp.RLock(),), initializer=tqdm.set_lock)
        all_workers = [pool.apply_async(worker, args=(process_num, process_songs[process_num])) for process_num in range(num_workers)]

        pool.close()

        results = [job.get() for job in all_workers]

        # Unpack the results from multiple workers.
        results = [item for sublist in results for item in sublist]

        # Save preprocessed songs from single file: ./preprocessed/ready_<id>.json
        with open('./preprocessed/ready_' + str(col_idx) + '.json', 'w') as file:
            json.dump(results, file)
            file.close()
        
        # Clear command line. Better display of multiprocessing progress in multiple batches.
        os.system('cls')