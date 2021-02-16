import argparse
import multiprocessing as mp

from src.utils   import split_dataset
from src.workers import preprocess_collection
from src.index   import build_index, partition_lexicon

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset',       nargs="?", type=str, help='Name of JSON file with the raw songs that you want to preprocess.')
    parser.add_argument('--split',         nargs="?", type=int, help='How many songs to preprocess at once. Should be tuned to your available RAM.',                                    default=200000)
    parser.add_argument('--num_processes', nargs="?", type=int, help='Number of threads you want to run.',                                                                              default=1)
    parser.add_argument('--num_indexes',   nargs="?", type=int, help='Number of files into which you want to partition your index. If index is to large its hard to load it into RAM.', default=1)

    return parser.parse_args()

def main():
    args = get_args()

    assert args.dataset[-5:] == '.json',         'Dataset must be a JSON file.'
    assert args.split > 0
    assert args.num_processes > 0,               'Number of processes must be at least 1.'
    assert args.num_processes <= mp.cpu_count(), 'Your computer supports at most ' + str(mp.cpu_count()) + ' processes.'
    assert args.num_indexes > 0

    split_dataset(args.dataset, args.split)
    preprocess_collection(args.num_processes)
    partition_lexicon(args.num_splits)
    build_index(args.num_indexes)

if __name__ == '__main__':
    mp.freeze_support()
    main()