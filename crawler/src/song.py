import requests
import re
import langdetect

from unidecode import unidecode
from bs4       import BeautifulSoup

# Object for storing song data. Convertible to dictonary via to_dict method.
class Song:

    # Song fields:
    #   url      - string - link to Genius song page.                  ***CURRENTLY TREATED AS SONG ID***
    #   lyrics   - string with lyrics.                                 ***CANNOT BE EMPTY***
    #   title    - string with title.                                  ***CAN BE EMPTY STRING***
    #   author   - tuple - (author_name, link_to_authors_genius_page)  ***ASSUMPTION - THERE IS ONLY ONE AUTHOR***
    #                                                                  ***CAN BE TUPLE OF TWO EMPTY STRINGS***
    #   language - string - detected language of song.                 ***CAN BE UNKNOWN***
    #   image    - string - link to cover image of song.
    #   album    - string - name of album
    #   video    - string - link to YouTube music video for song       ***CAN BE EMPTY***
    #   tags     - list of strings that represents categories of song.
    #   credits  - dictionary with song metadata. Each metadata name 
    #              is a string. Given metadata type can have multiple 
    #              values. A metadata value can refer to a Genius 
    #              page so it is a tuple.
    #
    #              Example:
    #              {'Written By': [['Crisis tha Sharpshooter', 'https://genius.com/artists/Crisis-tha-sharpshooter'],
    #                             ['Rugged Monk',             'https://genius.com/artists/Rugged-monk']],
    #               'Recorded At': [['Trickfingers Playhouse', '']],
    #               'Produced by': [['John Frusciante',        'https://genius.com/artists/John-frusciante']]}
    
    # Initialize with link to Genius song page. This page will be scraped.
    def __init__(self, link):
        self.url      = link
        request       = requests.get(link)
        html          = request.text
        self.lyrics   = self.extract_lyrics(html)
        self.credits  = {**self.extract_credits(html, 'credits'), **self.extract_credits(html, 'headers')}
        self.credits  = {**self.credits, **self.extract_credits(html, 'vol_2')}
        self.title    = self.extract_title(html)
        self.author   = self.extract_author(html)
        self.language = self.detect_language()
        self.image    = self.extract_image(html)
        self.album    = self.extract_album(html)
        self.video    = self.extract_video(html)
        self.tags     = self.extract_tags(html)
    
    def extract_lyrics(self, html):
        verses = BeautifulSoup(html, 'html.parser').find_all('div', {'class': 'Lyrics__Container-sc-1ynbvzw-2 jgQsqn'})

        if len(verses) == 0:
            verses = BeautifulSoup(html, 'html.parser').find_all('div', {'class': 'lyrics'})
            
        if len(verses) > 0:
            text = [verse.get_text(separator=' ') for verse in verses]

            # Remove empty strings - empty spaces between verses on webpage.
            text = [verse for verse in text if verse != '']
            text = ' '.join(text)

            # Remove HTML character encoding.
            text = unidecode(text)

            # Remove newlines.
            text = text.replace('\n', ' ')

            # Remove multiple consecutive spaces by single space.
            text = re.sub(' {2,}', ' ', text)

            # Remove initial space.
            if len(text) != 0 and text[0] == ' ':
                text = text[1:]

            # Remove trailing space
            if len(text) != 0 and text[-1] == ' ':
                text = text[:-1]

            return text
        
        return ''
    
    def extract_image(self, html):
        link = BeautifulSoup(html, 'html.parser').find('img', {'class': 'cover_art-image'})

        if link is None:
            link = BeautifulSoup(html, 'html.parser').find('img', {'class': 'SizedImage__NoScript-sc-1hyeaua-1 hYJUSb'})
            
        if link is not None:
            return link.get('src')
        
        return ""
    
    def extract_album(self, html):
        soup  = BeautifulSoup(html, 'html.parser')
        album = soup.find('div', {'class': 'HeaderTracklist__Album-sc-1qmk74v-3 hxXYDz'})

        if album is not None:
            return unidecode(album.text)

        album = soup.find_all('div', {'class': 'metadata_unit'})

        if len(album) > 0: 
            album = [meta.a.text for meta in album if 'Album' in meta.text]

            if len(album) > 0:
                return unidecode(album[0])

        return ''

    def extract_video(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        soup = soup.find('div', {'class': 'MusicVideo__Container-sc-1980jex-0 cYtdTH'})

        if soup is not None:
            return soup.iframe['src']
        
        yt_links = re.findall('http://www.youtube.com/watch.*?;', html)

        if len(yt_links) > 0:
            return yt_links[0][:-1]

        return ''

    def extract_tags(self, html):
        tags = [tag.group() for tag in re.finditer('https://genius.com/tags/.*?(\"|&)', html)]

        for idx, tag in enumerate(tags):
            if tag[-1] == '&':
                tags[idx] = tag[tag.rindex('/')+1:-1]

            else:
                tags[idx] = tag[tag.rindex('/')+1:-2]

        # Remove duplicate tags.
        tags = list(set(tags))

        return tags

    # Extract metadata. credit_type is either 'headers', 'credits' or 'vol_2'. If 'credits' extract 
    # metadata from bottom of Genius page. If 'headers' extract metadata from top of Genius page.
    # If 'vol_2' then different format of Genius webpage was returned so use different parsing.
    def extract_credits(self, html, credit_type):
        soup        = BeautifulSoup(html, 'html.parser')
        credit_dict = {}

        if credit_type == 'headers':
            credits = soup.find_all('div', {'class': 'HeaderMetadata__Section-sc-1p42fnf-2'})
        elif credit_type == 'credits':
            credits = soup.find_all('div', {'class': 'SongInfo__Credit-nekw6x-3 ftrCKq'})
        elif credit_type == 'vol_2':
            credits = soup.find_all('div', {'class': 'metadata_unit'})

        for credit in credits:
            if credit_type == 'headers':
                label = credit.find('p')
            elif credit_type == 'credits':
                label = credit.find('div', {'class': 'SongInfo__Label-nekw6x-2'})
            elif credit_type == 'vol_2':
                label = credit.find('span', {'class': 'metadata_unit-label'})
                
            if label is None:
                continue
            
            label = unidecode(label.text)
            vals  = credit.find_all('a')
                    
            if len(vals) == 0:
                if credit_type == 'vol_2':
                    val = credit.find('span', {'class': 'metadata_unit-info'}).text
                else:
                    val = credit.get_text(separator='\n').split('\n')[-1]
                
                val      = unidecode(val)
                val_list = [(val, '')]
            else:
                val_list = [(unidecode(val.text), val['href']) for val in vals]
                    
            credit_dict[label] = val_list
                    
        return credit_dict
    
    # Assumes that title is in the first <h1></h1> on the lyrics page.
    def extract_title(self, html):
        soup  = BeautifulSoup(html, 'html.parser')
        title = soup.find_all('h1')

        if len(title) > 0:
            return unidecode(title[0].get_text())
        
        # If title was not found return empty string.
        return ''
    
    # Assumes that author is in the first <a></a> with SongHeader__Artist-sc-1b7aqpg-9 class. Also
    # assumes there is only one author. Remaining authors are in the credits dictionary. Also 
    # extracts a link to author's genius page.
    def extract_author(self, html):
        soup   = BeautifulSoup(html, 'html.parser')
        author = soup.find_all('a', 'SongHeader__Artist-sc-1b7aqpg-9')
        
        if len(author) > 0:
            author = author[0]
            ref    = author['href']
            author = author.get_text()
            author = unidecode(author)
        
            return author, ref

        author = soup.find('h2')

        if author is not None:
            ref    = author.a['href']
            author = author.text
            author = author.replace('\n', '')
            author = unidecode(author)

            return author, ref
        
        # If author was not found return two empty strings.
        return '', ''
    
    def detect_language(self):
        try:
            return langdetect.detect(self.lyrics)
        except:
            return 'unknown'
    
    # Converts the song object into a dictionary that can easily be saved as JSON object.
    def to_dict(self):
        obj              = dict()
        obj['url']       = self.url
        obj['title']     = self.title
        obj['author']    = self.author
        obj['lyrics']    = self.lyrics
        obj['credits']   = self.credits
        obj['language']  = self.language
        obj['image_url'] = self.image
        obj['album']     = self.album
        obj['video_url'] = self.video
        obj['tags']      = self.tags
        
        return obj