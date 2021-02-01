import requests
import re
import langdetect

from bs4 import BeautifulSoup

# Object for storing song data. Convertible to dictonary via to_dict method.
class Song:

    # Song fields:
    #   url     - string - link to Genius song page.                 ***CURRENTLY TREATED AS SONG ID***
    #   lyrics  - string with lyrics.                                ***CANNOT BE EMPTY***
    #   title   - string with title.                                 ***CAN BE EMPTY STRING***
    #   author  - tuple - (author_name, link_to_authors_genius_page) ***ASSUMPTION - THERE IS ONLY ONE AUTHOR***
    #                                                                ***CAN BE TUPLE OF TWO EMPTY STRINGS***
    #   credits - dictionary with song metadata. Each metadata name 
    #             is a string. Given metadata type can have multiple 
    #             values. A metadata value can refer to a Genius 
    #             page so it is a tuple.
    #
    #             Example:
    #             {'Written By': [['Crisis tha Sharpshooter', 'https://genius.com/artists/Crisis-tha-sharpshooter'],
    #                             ['Rugged Monk',             'https://genius.com/artists/Rugged-monk']],
    #              'Recorded At': [['Trickfingers Playhouse', '']],
    #              'Produced by': [['John Frusciante',        'https://genius.com/artists/John-frusciante']]}
    #

    
    # Initialize with link to Genius song page. This page will be scraped.
    def __init__(self, link):

        self.url      = link
        request       = requests.get(link)
        html          = request.text
        self.lyrics   = self.extract_lyrics(html)
        self.credits  = {**self.extract_credits(html, 'credits'), **self.extract_credits(html, 'headers')}
        self.title    = self.extract_title(html)
        self.author   = self.extract_author(html)
        self.language = self.detect_language()
        
    # Extracts plain string verse from the Genius HTML version.
    def html_to_verse(self, html_verse):
        verse = re.findall('>.*?<', html_verse)
        verse = [sentence[1:-1] for sentence in verse if len(sentence) > 2]

        return ' '.join(verse)
    
    def extract_lyrics(self, html):
        verses = re.findall('<div class="Lyrics__Container-sc-1ynbvzw-2 jgQsqn">.*?</div>', html)
        lyrics = []

        for html_verse in verses:
            lyrics += [self.html_to_verse(html_verse)]
            
        if len(lyrics) == 0:
            verses = BeautifulSoup(html, "html.parser").find("div", {"class": "lyrics"})
            if (verses is None):
                return ''
            text = verses.text
            text = text.replace('\n', ' ')
            return text

        return ' '.join(lyrics)
    
    # Extract single type of metadata.
    def extract_credit(self, html, credit_type):
        fields     = re.findall('>.*?</', html)
        field_vals = []

        if credit_type == 'credits':
            fields     = [field[1:-2] for field in fields if len(field) > 3]
            field_name = fields[0]
        elif credit_type == 'headers':
            field_name = fields[0][fields[0].rindex('>')+1:-2]

        for value in range(1, len(fields)):
            field     = fields[value]
            reference = re.findall('href=".*?"', field)

            if credit_type == 'credits':
                field_val = field[field.index('>')+1:]
            elif credit_type == 'headers':
                field_val = field[field.rindex('>')+1:-2]
    
            if len(reference) == 0:
                field_vals += [(field_val, '')]
            else:
                field_vals += [(field_val, reference[0][6:-1])]
            
        return field_name, field_vals

    # Extract metadata. credit_type is either 'headers' or 'credits'. If 'credits' extract metadata
    # from bottom of Genius page. If 'headers' extract metadata from top of Genius page.
    def extract_credits(self, html, credit_type):
        if credit_type == 'headers':
            credits = re.findall('<div class="HeaderMetadata__Section-sc-1p42fnf-2 hAhJBU">.*?</div>', html)
        elif credit_type == 'credits':
            credits = re.findall('<div class="SongInfo__Label-nekw6x-2 hlmwHa">.*?</div>.*?</div>', html)

        text_data = dict()

        for credit in credits:
            key, value     = self.extract_credit(credit, credit_type)
            text_data[key] = value

        return text_data
    
    # Assumes that title is in the first <h1></h1> on the lyrics page.
    def extract_title(self, html):
        soup  = BeautifulSoup(html, 'html.parser')
        title = soup.find_all('h1')

        if len(title) > 0:
            return title[0].get_text()
        
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
        
            return author, ref
        
        # If author was not found return two empty strings.
        return '', ''
    
    def detect_language(self):
        if self.lyrics == '':
            return ''
        else:
            return langdetect.detect(self.lyrics)
    
    # Converts the song object into a dictionary that can easily be saved as JSON object.
    def to_dict(self):
        obj             = dict()
        obj['url']      = self.url
        obj['title']    = self.title
        obj['author']   = self.author
        obj['lyrics']   = self.lyrics
        obj['credits']  = self.credits
        obj['language'] = self.language
        
        return obj