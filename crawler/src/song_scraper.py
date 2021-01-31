import math
import json
import multiprocessing as mp

from pathlib   import Path
from src.song  import Song
from src.utils import garbage_collector, combine_results

def scraper(process_num):

    # Get links designated for the process.
    with open('./temporary/links/links_' + str(process_num) + '.txt', 'r') as file:
        links = [line[:-1] for line in file]

        file.close()
    
    for idx, link in enumerate(links):

        # Scrape the Genius lyrics page.
        song = Song(link)

        # Sometimes the requests fail. If this happens do not save the song.
        if len(song.lyrics) > 0:

            # Save the song in the form of dictionary in a JSON file.
            file_name  = './temporary/songs/' + str(process_num) + '_' + str(idx) + '.json'

            with open(file_name, 'w') as outfile:
                json.dump(song.to_dict(), outfile)

                outfile.close()
        else:

            # Request failed and the song cannot be scraped. Save the link to the song to try to
            # scrape it later.
            with open('./temporary/bad_links/bad_links_' + str(process_num) + '.txt', 'a') as file:
                file.write(link + '\n')
                    
                file.close()

# Split the song links equally among the processes.
# link_file - .txt file with all song links to be scraped.
# output    - num_processes of links_{process_number}.txt files in the temporary/links directory. 
#             Each file has equal amount of links, one link per line. Links in this file are 
#             designated to corresponding process.
def divide_links(link_file, num_processes):
    with open(link_file, 'r') as file:
        links = [line for line in file]

        file.close()

    interval = int(math.ceil(len(links) / num_processes))

    # If temporary/links directory does not exist in current directory, create it.
    Path('./temporary/links').mkdir(exist_ok=True)

    for process in range(num_processes):
        process_links = links[process*interval:(process+1)*interval]
        process_links = ''.join(process_links)
        
        # Create file with song links designated for given process.
        with open('./temporary/links/links_' + str(process) + '.txt', 'w') as file:
            file.write(process_links)
            
            file.close()

def scrape_songs(link_file, num_processes):

    # Split links equally among processes.
    divide_links(link_file, num_processes)

    all_processes = [mp.Process(target=scraper, args=(process_num,)) for process_num in range(num_processes)]

    # If temporary/songs or temporary/bad_links directory does not exist in current directory, 
    # create it.
    Path('./temporary/songs').mkdir(exist_ok=True)
    Path('./temporary/bad_links').mkdir(exist_ok=True)

    for process in all_processes:
        process.start()

    for process in all_processes:
        process.join()

    # Combine results from all thread into one file in the outputs diractory.
    combine_results('songs')
    combine_results('bad_links')

    # Remove all files from temporary directory.
    garbage_collector()