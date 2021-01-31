import argparse

from src.link_crawler import gather_song_links
from src.song_scraper import scrape_songs

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--type',          nargs="?", type=str, help='link_crawl or song_crawl. Use link_crawl to gather links at which genius songs can be located. Use song_crawl to scrape songs from links provided in link_file.')
    parser.add_argument('--num_processes', nargs="?", type=int, help='Number of threads you want to run.', default=1)
    parser.add_argument('--start',         nargs="?", type=int, help='Only with link_crawl, id of page from which lyrics crawling should start.')
    parser.add_argument('--end',           nargs="?", type=int, help='Only with link_crawl, id of page on which crawling should stop. (exclusive)')
    parser.add_argument('--links_file',    nargs="?", type=str, help='Only with song_crawl. Specifies file with links of songs that should be scraped.')

    return parser.parse_args()

def main():
    args = get_args()

    assert args.num_processes > 0,                    'ERROR: --num_processes must be positive.'
    assert args.type in ['link_crawl', 'song_crawl'], 'ERROR: Please specify link_crawl or song_crawl for type --flag.'

    if args.type == 'link_crawl':
        assert args.start != None,    'ERROR: when using link_crawl --start must be specified.'
        assert args.start >= 0,       'ERROR: --start must be nonnegative.'
        assert args.end != None,      'ERROR: when using link_crawl --end must be specified.'
        assert args.end > args.start, 'ERROR: --end must be greater than start.'

        gather_song_links(args.start, args.end, args.num_processes)

    elif args.type == 'song_crawl':
        assert args.links_file != None,        'ERROR: when using song_crawl --links_file must be specified.'
        assert args.links_file[-4:] == '.txt', 'ERROR: --links_file must be a .txt file.'

        scrape_songs(args.links_file, args.num_processes)

if __name__ == '__main__':
    main()