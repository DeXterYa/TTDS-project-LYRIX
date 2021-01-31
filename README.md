# :spider: GENIUS CRAWLER
Built for multithreading.

### Crawler structure:
```
crawler
├── outputs
├── src
│   ├── link_crawler.py
│   ├── song.py
│   ├── song_scraper.py
│   └── utils.py
├── temporary
│   ├── bad_links
│   ├── songs
│   └── links
├── crawl.py
└── example.json
```
#### Notes:
* You probably should not touch the `crawler/temporary` directory. It stores the intermediate results of crawling that each thread makes. When all processes finish the files will be removed from this directory. *(thus, temporary name, duh...)*
* crawl.py is the runner.
* The final results of crawling will be stored in the outputs directory, and they will combine results from all of the threads.
* Each final result is assingned a new id, so you do not need to worry that it will overwrite your previous results.
## Two modes of crawling
#### Link crawl
Crawls lists of Genius songs such as this: https://genius.com/artists/songs?for_artist_page=1 and extracts the links. The links are saved in `crawler/outputs/all_links_{id}.txt` file, link at a line. Some of such pages are empty. 
#### Song crawl
Given `.txt` file with links to pages with Genius lyrics, scrapes the songs' data. There should be one link at a line in the input file. *(Inteded Use: the output of link crawl should be input of song crawl)* Saves the songs in `crawler/outputs/all_songs_{id}.json` file. The `all_songs.json` file is a list of dictionaries that represent a song. Example of JSON object that represents a song can be found in `crawler/example.json`. The requests sometimes fail, so crawler also saves the links on which scraping failure occured in `crawler/outputs/all_bad_links_{id}.txt` file. *(Currently about half of reuqests fail)* Scraping songs from this file often succeeds later.

Example link to Genius lyrics:
https://genius.com/Kanye-west-lift-yourself-lyrics
## How to run
To run the crawler you **MUST** be in the crawler directory.
`cd crawler`
Example uses:
`python crawl.py --type link_crawl --start 0 --end 100 --num_processes 10`
`python crawl.py --type song_crawl --links_file ./outputs/all_links_0.txt --num_processes 10`
#### Inputs
1. `--type` - song_crawl or link_crawl
2. `--num_processes` - number of threads on which you want to run the crawler. Default = 1.
3. `--start` - Only for link_crawl. Defines the {page_id} of genius page with list of links from which crawling should start.  https://genius.com/artists/songs?for_artist_page={page_id}. *(inclusive)*
4. `--end` - Only for link_crawl. Defines the {page_id} of genius page with list of links on which crawling should end. https://genius.com/artists/songs?for_artist_page={page_id}. *(exclusive)*
5. `--links_file` - Only for song_crawl. `.txt` file with links to Genius song pages. One link at a line.

## TO DO:
- [ ] Extract song image
- [ ] Extract name of song album
- [ ] Extract tags
- [ ] Extract song language *(possibly add multithreading language detection module)*
