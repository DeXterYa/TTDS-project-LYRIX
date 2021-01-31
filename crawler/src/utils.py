import os
import json
import glob

from pathlib import Path

# Remove all files from temporary directory.
def garbage_collector():

    Path('./temporary').mkdir(exist_ok=True)
    Path('./temporary/links').mkdir(exist_ok=True)
    Path('./temporary/songs').mkdir(exist_ok=True)
    Path('./temporary/bad_links').mkdir(exist_ok=True)

    for file_type in ['links', 'songs', 'bad_links']:
        path = './temporary/' + file_type + '/'

        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)

            os.unlink(file_path)

# Combines results produced by multiple threads into one file in the outputs directory. results_type
# is 'songs', 'links', or 'bad_links'.
def combine_results(results_type):
    if results_type == 'links':
        directory = 'links/links_*.txt'
    elif results_type == 'songs':
        directory = 'songs/*.json'
    elif results_type == 'bad_links':
        directory = 'bad_links/bad_links_*.txt'
    
    file_list  = glob.glob('./temporary/' + directory)
    collection = []

    # Extract all of the gathered links.
    for temporary_file in file_list:
        with open(temporary_file, 'r') as file:
            if 'links' in results_type:
                collection += [line[:-1] for line in file]
            elif results_type == 'songs':
                collection += [json.loads([line for line in file][0])]

            file.close()

    if 'links' in results_type:

        # Remove duplicate links.
        collection = list(set(collection))

        # Separate links by one newline.
        collection = '\n'.join(collection)

    # If outputs directory does not exist in current directory, create it.
    Path('./outputs').mkdir(exist_ok=True)

    # Find id of last created file in the output files.
    previous_files = glob.glob('./outputs/all_' + results_type + '_*')

    if len(previous_files) == 0:
        new_id = 0
    else:
        skip = len('./outputs\\all_' + results_type + '_')

        if results_type == 'songs':
            end_skip = -5
        elif 'links' in results_type:
            end_skip = -4

        previous_ids = [int(file[skip:end_skip]) for file in previous_files]
        new_id       = max(previous_ids) + 1

    file_name = './outputs/all_' + results_type + '_' + str(new_id)

    if results_type == 'songs':
        file_name += '.json'
    elif 'links' in results_type:
        file_name += '.txt'

    # Save results into one file.
    with open(file_name, 'w') as file:
        if results_type == 'songs':
            json.dump(collection, file)
        elif 'links' in results_type:
            file.write(collection)

        file.close()