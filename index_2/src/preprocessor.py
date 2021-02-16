import re

from nltk import SnowballStemmer

class Preprocessor:

    # Initializes all stemmers.
    def __init__(self):

        # List of languages we intend to support.
        languages  = ['danish', 'dutch', 'english', 'finnish', 'french', 'german', 'hungarian'] 
        languages += ['italian', 'norwegian', 'portuguese', 'romanian', 'spanish', 'swedish']
        stemmers   = dict()

        # Maps languages we intend to support to their ISO 639-1 codes.
        lang_to_iso = {'danish':     'da',
                       'dutch':      'nl',
                       'english':    'en', 
                       'finnish':    'fi', 
                       'french':     'fr', 
                       'german':     'de', 
                       'hungarian':  'hu', 
                       'italian':    'it', 
                       'norwegian':  'no', 
                       'portuguese': 'pt', 
                       'romanian':   'ro', 
                       'spanish':    'es', 
                       'swedish':    'sv'}

        # stemmers maps ISO 639-1 language code string to corresponding NLTK Snowball stemmer.
        for lang in languages:
            stemmers[lang_to_iso[lang]] = SnowballStemmer(lang)

        self.stemmers = stemmers

    # Input txt is a string. Removes space from begining and end of that string. Also removes space
    # that occur more than once, consequitively. Outputs resulting string.
    def remove_multi_space(self, txt):

        # Remove consecutive spaces.
        txt = re.sub(' {2,}', ' ', txt)

        # Remove space from end of string.
        if len(txt) > 0 and txt[0] == ' ':
            txt = txt[1:]

        # Remove space from begining of string.
        if len(txt) > 0 and txt[-1] == ' ':
            txt = txt[:-1]
            
        return txt

    # Preprocess txt string. Has 3 modes of working depending on value of of_type variable.
    #   of_type == song  - Applies stemming in only the language of the song. If this option 
    #                      is chosen lang variable must be provided and it must correspond to the 
    #                      ISO 639-1 encoding of one of the supported languages.
    #   of_type == query - Applies stemming with all available stemmers, creates set of resultant 
    #                      stems and input word forms, then returns string with all possible word 
    #                      forms sorted in alphabetical order.
    #   of_type == other - Does not apply any stemming, just tokenizes the txt string, removes 
    #                      nonalphanumeric characters and does not do anything more.
    #   output           - Preprocessed string without begining or trailing spaces, all words 
    #                      separated by single space.
    def preprocess(self, txt, of_type, lang='unknown'):

        # Ensures propper processing of queries. (Otherwise pattern might not match)
        txt = ' ' + txt + ' '

        # Defensive programming.
        assert of_type in ['song', 'query', 'other'], 'Unknown type: ' + str(of_type)

        if of_type == 'song':
            assert lang in self.stemmers, 'Unknown language: ' + str(lang)

        # Case folding.
        txt = txt.lower()

        # Removes non-alphanumeric letters.
        # Maintains numbers.
        # If token is separated by non-alphanumeric characters that are not space then maintains its 
        # two versions in the BOW string representation. Examples:
        #   - i'm             - saves im and i m number of times i'm occurs in text
        #   - 34+45           - saves 34 35 and 3435
        #   - ph.d.           - saves ph d and phd
        #   - g.o.a.t.        - saves g o a t and goat
        #   - (0131)-xxx-aaaa - saves 0131 xxx aaaa and 0131xxxaaaa
        # In this way whatever form user types as query he is going to have a match.
        pattern  = ' [^ a-z0-9]*[a-z0-9]+([^ a-z0-9]+[a-z0-9]+)+[^ a-z0-9]* '
        expand   = [re.sub('[^a-z0-9]', '', txt[match.start():match.end()]) for match in re.finditer(pattern, txt)]
        txt     += ' ' + ' '.join(expand)

        # Remove non-alphanumeric characters.
        txt = re.sub('[^a-z0-9 ]', ' ', txt)
        txt = self.remove_multi_space(txt)

        if of_type == 'other':
            return txt

        txt = txt.split()

        if of_type == 'query':
            expand = []

        for idx, word in enumerate(txt):

            if of_type == 'song':

                # Stem word with stemmer of song language.
                txt[idx] = self.stemmers[lang].stem(word)

            elif of_type == 'query':

                # Stem word with every available stemmer.
                for stemmer in self.stemmers.values():
                    expand += [stemmer.stem(word)]

        if of_type == 'query':

            # Multiple stemmers can map same word to same stem, so remove duplicates, Also maintain 
            # input forms.
            txt = list(set(expand).union(set(txt)))

            # Sort words in alphabetical order.
            txt.sort()

        txt = ' '.join(txt)

        return txt