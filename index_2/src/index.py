import json
import os

from glob        import glob
from tqdm        import trange
from collections import Counter, OrderedDict
from sys         import getsizeof
from math        import ceil

# Computes the lexicon of whole dataset. Scans the files in the preprocessed directory which should
# hold songs in inverted index format. The lexicon has a form of dictionary in which keys are the
# terms in the dataset, soreted in alphabetical order. The values are the document frequencies
# of the terms.
def compute_lexicon():
    file_list = glob('./preprocessed/*.json')
    lexicon   = Counter()
    num_files = len(file_list)

    for file_idx in trange(num_files, desc='Computing lexicon'):
        ready = file_list[file_idx]

        with open(ready, 'r') as file:
            docs = json.loads([line for line in file][0])

            file.close()

        doc_lex = []
        
        for document in docs:
            doc_lex += list(document.keys())

        lexicon += Counter(doc_lex)
    
    lexicon = dict(OrderedDict(sorted(lexicon.items())))

    return lexicon

# Splits the lexicon into num_splits partitions. In this way the inverted index for the whole 
# dataset can be separated into a num_splits files. Saves each list of words for given index file
# in a split_<index_file_id>.json file in lexicon_splits dataset.
# *** SUGESTED NUMBER OF SPLITS - AT LEAST 10 *** (If you use less your RAM will expload, I have 
# 16 GB RAM, if you have less you should use even more splits.)
def partition_lexicon(num_splits):
    lexicon   = compute_lexicon()

    # Split the lexicon so that sum of document frequencies of all terms in a split is similar.
    # (size of inverted index for a term is proportional to the number of documents in which it
    # occurs - document frequency.)
    split_val = sum(list(lexicon.values())) / num_splits
    splits    = [[] for i in range(num_splits)]
    N         = len(lexicon)
    lexicon   = list(lexicon.items())
    split_idx = 0
    val_cnt   = 0

    for idx in range(N):
        word = lexicon[idx][0]

        # val_cnt is the document frequency sum for the current split. If it exceeds split_val, the 
        # split already has enough words, so start to accumulate terms in next split.
        if val_cnt >= split_val:
            split_idx += 1

            # Reset the cumulative document frequency for the split.
            val_cnt = 0
            
        # Add word to split and increase the accumualted document frequency.
        splits[split_idx] += [word]
        val_cnt           += lexicon[idx][1]

    # Save each split in appropriate JSON file.
    for idx in range(num_splits):
        with open('./lexicon_splits/split_' + str(idx) + '.json', 'w') as file:
            json.dump(splits[idx], file)
            file.close()

# Builds inverted index from collection of inverted index representations of singular songs in the
# files in preprocessed directory. The overall index is saved in a set of index_<id>.json files
# in the indexes directory.
# *** SUGESTED NUMBER OF SPLITS - AT LEAST 10 *** (If you use less your RAM will expload, I have 
# 16 GB RAM, if you have less you should use even more splits.)
def build_index(num_splits):
    file_list = glob('./preprocessed/*.json')

    for split_idx in trange(num_splits, desc='Index files ready'):

        # Load set of terms for which the index is currently build.
        with open('./lexicon_splits/split_' + str(split_idx) + '.json', 'r') as file:
            split = json.loads([line for line in file][0])

            file.close()
        
        index = dict()

        # Initialize the index for fast access.
        for word in split:
            index[word] = []

        N = len(file_list)

        for file_idx in trange(N, desc='Index file: ' + str(split_idx+1) + ', preprocessed file'):
            file_name = file_list[file_idx]

            # Load file from preprocessed directory.
            with open(file_name, 'r') as file:
                docs = json.loads([line for line in file][0])

                file.close()

            for doc in docs:
                for word in doc:

                    # Check if the word is in a split for which we are currently building a index.
                    if split[0] <= word and word <= split[-1]:
                        index[word] += [doc[word]]

        index = list(index.items())

        # Convert index into a set of dictionaries easy to translate into MongoDB documents.
        # A dictionary has 't' field for term and 'p' field for postings. 'p' is a list of of lists.
        # each list in 'p' has two values. The first value is the song ID, the second term is the
        # term frequency in that song.
        for idx, term in enumerate(index):
            index[idx]      = dict()
            index[idx]['t'] = term[0]
            index[idx]['p'] = term[1]

        expand = []

        # Documents larger than 16 MB cannot be saved in the MongoDB. Documents for some stop words
        # are that big. Thus, I split them into a number of documents, that have same 't' field 
        # value, but the 'p' list is split among them.
        for term in index:

            # I have empirically found that when this condition is True the document has more than
            # 16 MB.
            if getsizeof(term['p']) > 4688312:

                # Compute to how many partitions the document should be divided so that none of the
                # partitions exceeds 16 MB.
                num_partitions = int(ceil(getsizeof(term['p']) / 4688312))

                # Interval is the number of 'p' list values per partition.
                interval = int(ceil(len(term['p']) / num_partitions))
                
                # Create partitions.
                for i in range(num_partitions):
                    new_term       = {'t': term['t']}
                    new_term['p']  = term['p'][i*interval:(i+1)*interval]
                    expand        += [new_term]

        # Replace the large documents by their partitions.   
        index  = [term for term in index if getsizeof(term['p']) <= 4688312]
        index += expand

        # Sort the index by 't' field.
        index = sorted(index, key=lambda term: term['t'])

        with open('./indexes/index_' + str(split_idx) + '.json', 'w') as file:
            json.dump(index, file)
            file.close()

        # Clear the command line output.
        os.system('cls')