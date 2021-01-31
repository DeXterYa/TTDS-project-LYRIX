import requests
import math
import multiprocessing as mp

from bs4       import BeautifulSoup
from pathlib   import Path
from src.utils import garbage_collector, combine_results

# Gathers links to Genius songs which can be found under this link: 
# https://genius.com/artists/songs?for_artist_page={page_number}
# To run correctly there must be temporary/links directory in the current directory.
# Inputs:
#   start       - {page_number} from which thread should start crawling.
#   interval    - number of pages the crawler should scrape
#   process_num - the id of the thread
# Output:
#   links_{process_num}.txt - File located in temporary/links directory. Each link occupies one line 
#                             in the file.
def crawl_songs_links(start, interval, process_num):
    base_link = 'https://genius.com/artists/songs?for_artist_page='

    with open('./temporary/links/links_' + str(process_num) + '.txt', 'w') as file:

        for page_idx in range(start, start + interval):
            html = requests.get(base_link + str(page_idx)).text
            soup = BeautifulSoup(html, 'html.parser')

            for link in soup.find_all('a', 'song_name'):
                file.write(link['href'] + '\n')
                
        file.close()

# Crawls the https://genius.com/artists/songs?for_artist_page={page_number} pages to extract links
# to song lyrics.
# Inputs:
#   start        - page_number from which crawling should start. (inclusive)
#   end          - page_number at which crawling should end. This page will not be crawled. (exclusive)
#   num_pocesses - number of threads to use.
# Output:
#   all_links_{id}.txt - File in outputs directory with all extracted links. One link per line.
def gather_song_links(start, end, num_processes):

    # If temporary/links directory does not exist in current directory, create it.
    Path('./temporary/links').mkdir(exist_ok=True)

    # interval is number of pages with links to songs lyrics that each thread should crawl.
    interval      = int(math.ceil((end - start) / num_processes))
    all_processes = []

    for process_num in range(num_processes - 1):
        start_idx      = start + interval * process_num
        all_processes += [mp.Process(target=crawl_songs_links, args=(start_idx, interval, process_num))]

    # If the number of pages to crawl is not divisible by number of processes then the last process
    # should crawl smaller number of pages.
    last_interval  = (end - start) - (num_processes - 1) * interval
    start_idx      = start + interval * (num_processes - 1)
    all_processes += [mp.Process(target=crawl_songs_links, args=(start_idx, last_interval, num_processes - 1))]

    # Start processes.
    for process in all_processes:
        process.start()

    # Finish processes.
    for process in all_processes:
        process.join()

    # Combine results of mulitple threads into one file, remove temporary files.
    combine_results('links')
    garbage_collector()