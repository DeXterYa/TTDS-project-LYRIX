# by:             Marcin Rybok
# student number: s1766172

from sys              import argv
from re               import sub
from nltk.stem.porter import PorterStemmer
from math             import log10
from collections      import OrderedDict
from numpy            import argsort
from numpy            import array
from json             import loads
from json             import dump
from tqdm             import trange

# Class for preprocessing text. Applies case folding, tokenization and stemming and
# outputs preprocessed text in a uniform format. Has 1 field:
# - stemmer - PorterStemmer from NLTK library - initialized when object is created.
class Preprocessor:
    
    def __init__(self):
        self.stemmer = PorterStemmer()
    
    # Takes a string, tokenizes it. Outputs the string after tokenization. The input txt string 
    # should be already case folded.
    def tokenize(self, txt):
        
        # Remove all nonletter characters.
        txt = sub("[^a-zA-Z ]+", ' ', txt)
        
        return txt
    
    # Applies all steps of text preprocessing to the provided txt string. Applies case folding,
    # tokenization and stemming. Outputs the resultant preprocessed string.
    def preprocess(self, txt):

        # Apply case folding
        txt = txt.lower()

        # Tokenize the text.
        txt = self.tokenize(txt)

        # Apply stemming to the tokenized text.
        txt = self.stem(txt)

        return txt
        
    # Applies stemming to provided string txt. The provided string should be already case folded 
    # and tokenized. Outputs string after stemming. Uses PorterStermmer from the NLTK library.
    def stem(self, txt):
        txt = txt.split()
        
        for idx, word in enumerate(txt):
            txt[idx] = self.stemmer.stem(word)
                
        txt = ' '.join(txt)

        # Ensures that all strings produced by stem have the same format: The string starts 
        # and ends with a letter and all words in the txt are separated by a single space. Makes 
        # outputs more uniform and easier to process further.
        txt = self.removeMultiSpace(txt)
        
        return txt

    # Makes strings more uniform. Removes multiple consecutive occurrences of space by single space 
    # in provided txt string. Also removes space from the beginning and end of the provided string.
    # Outputs resultant string.
    def removeMultiSpace(self, txt):

        # Replace ale multiple occurrences of space by single space.
        txt = sub(' {2,}', ' ', txt)
        
        # Remove space from the beginning of a string.
        if len(txt) != 0 and txt[0] == ' ':
            txt = txt[1:]

        # Remove space from the end of a string. 
        if len(txt) != 0 and txt[-1] == ' ':
            txt = txt[:-1]
        
        return txt

# Class used for building index and searching the text collection. Has 2 fields:
# - preprocessor - an instance of the Preprocessor class. Used to preprocess the text collection 
#                  when index is built and for the preprocessing of queries.
# - index        - Dictionary maps each term to a dictionary that maps a document ID to the
#                  term frequency of that term in that document. To get document frequency just
#                  compute len(index[term]). The total number of documents is stored under a special
#                  name DOCUMENT_COUNT.
class SearchEngine:
    
    def __init__(self):
        self.preprocessor = Preprocessor()
            
    # Loads index from ready .json file. Populates the index field of the SearchEngine object.
    def loadIndex(self, fileName):
        with open(fileName, 'r') as file:
            self.index = loads([line for line in file][0])
            
            file.close()

    # Loads a dataset from .json file. The dataset should have a form of dictionary in which each
    # song ID is mapped to the song object.
    # Outputs:
    #   - texts  - list of songs lyrics
    #   - docNos - list with IDs of documents. texts[i] is the lyrics conentent of a song with 
    #              docNos[i] ID.
    # TO DO:
    # Currently builds index only from lyrics field. Enable searching on other metadata too.
    def loadDataset(self, fileName):
        with open(fileName, 'r') as file:
            songs = loads([line for line in file][0])

            file.close()

        docNos = list(songs.keys())
        texts  = [song['lyrics'] for song in songs.values()]

        return texts, docNos
    
    # Takes the name of .json file - inName and extract lyrics from such file. The json file should 
    # hold a dictionary of songs in which each song ID is mapped to a song object. The function 
    # builds an index from such file and saves it in the outFile. Populates the index and field 
    # of the SearchEngine object.
    def buildIndex(self, inFile, outFile):
        self.index    = dict()
        texts, docNos = self.loadDataset(inFile)

        # DOCUMENT_COUNT is a special entry in the index data structure that stores the total number
        # of documents.
        self.index['DOCUMENT_COUNT'] = len(docNos)
        
        # Preprocess each document.
        for txt_idx in trange(len(texts), desc='Preprocessing: '):
            txt            = texts[txt_idx]
            txt            = self.preprocessor.preprocess(txt)
            texts[txt_idx] = txt

        # Get the text of all collection.
        collection = ' '.join(texts).split()

        # Compute the lexicon of the whole collection.
        lexicon = list(set(collection))

        # For each document compute its lexicon - inefficient in space but increases the speed
        # of index building significantly.
        sets = [set(text.split()) for text in texts]

        # Ensures that index is sorted by term.
        lexicon.sort()

        # Word at a time index building.
        for word_idx in trange(len(lexicon), desc='Index building: '):
            word      = lexicon[word_idx]

            # Dictionary which maps each document ID to number of times a given term occurs in it.
            termFreqs = dict()

            for idx, text in enumerate(texts):

                # Checks if a word is in the lexicon of a given document - way faster than checking 
                # if word is in the entire text of the document.
                if word in sets[idx]:

                    # Compute number of times word occurs in a document with docNos[idx] id.
                    termFreq               = len([1 for term in text.split() if term == word])
                    termFreqs[docNos[idx]] = termFreq

            self.index[word] = termFreqs
        
        # Saves the built index into outFile.
        self.saveIndex(outFile)
    
    # Saves inverted index into a file specified by outFile name. 
    def saveIndex(self, outFile):
        with open(outFile, 'w') as file:
            dump(self.index, file)
            file.close()
    
    # Performs ranked search for the query string. Outputs list of most relevant documents.
    def rankedSearch(self, query):

        # Preprocess the query.
        query = self.preprocessor.preprocess(query)

        # Get dictionary in which each document id is mapped to its score for the query.
        scores = self.computeTFIDFs(query.split())

        # Sort the documents by their scores in descending order. Ensure that if two documents have 
        # the same score the one with lower document id occurs first in the output.
        scores     = OrderedDict(sorted(scores.items())[::-1])
        idx        = list(argsort(list(scores.values()), kind='stable'))[::-1]
        sortedDocs = list(array(list(scores.keys()))[idx])

        return sortedDocs
    
    # Computes the TFIDF score for each document that contains one of the provided query terms.
    # Result is returned in a dictionary in which each document id is mapped to its score for the
    # query with specified terms. The terms should result from preprocessing the original query.
    def computeTFIDFs(self, terms):
        N      = self.index['DOCUMENT_COUNT']
        scores = {}

        for term, postings in self.index.items():
            if term in terms:

                # len(postings) is the document frequency of given term.
                idf = log10(N / len(postings))

                # Iterate over documents that contain the word.
                for docId, termFreq in postings.items():
                    tf     = 1 + log10(termFreq)
                    weight = tf * idf

                    if docId not in scores:
                        scores[docId] = 0
                        
                    scores[docId] = scores[docId] + weight

        return scores