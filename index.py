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

# Class used to represent the inverted index for the single word. It has 3 fields:
# - term         - the stem of a word for which the inverted index is built.
# - documentFreq - number of documents in which the term occurs
# - termFreqs    - dictionary in which each key is a document id. The value for a specific key 
#                  is the term frequency in that document.
class TermIndex:
    
    def __init__(self, term=''):
        self.term         = term
        self.documentFreq = 0
        self.termFreqs    = {}
        
    # Converts string into a TermIndex object. Used to build an index from the already saved index. 
    # Returns the resulting TermIndex object.
    def fromString(self, idxTxt):
        first             = idxTxt.index(':')
        firstNewline      = idxTxt.index('\n')
        self.term         = idxTxt[:first]
        self.documentFreq = int(idxTxt[first+1:firstNewline])
        idxTxt            = idxTxt[firstNewline+1:]
        termFreqs         = idxTxt.split('\n')[:-1]
        
        for termFreq in termFreqs:
            first                 = termFreq.index(':')
            docNo                 = int(termFreq[1:first])
            freq                  = int(termFreq[first+2:])
            self.termFreqs[docNo] = freq
            
        return self
        
    # Converts the index into a string and returns it.
    def toString(self):
        indexString = self.term + ':' + str(self.documentFreq) + '\n'
        
        for docId, termFrequency in self.termFreqs.items():
            indexString += '\t' + str(docId) + ': ' + str(termFrequency) + '\n'
            
        return indexString

# Class used for building index and searching the text collection. Has 3 fields:
# - preprocessor - an instance of the Preprocessor class. Used to preprocess the text collection 
#                  when index is built and for the preprocessing of queries.
# - docNos       - list of document ids in the collection.
# - index        - list of TermIndex objects.
class SearchEngine:
    
    # Builds index. fileName - the name of a file from which the index should be built. indexReady 
    # is boolean which indicates if the index was already built and saved in a file such 
    # as 'index.txt'. To load the already saved index provide fileName that ends with .txt.
    # In such case indexReady should be True. To build an index from scratch pass indexReady 
    # as False and name of .json file as fileName.
    def __init__(self, fileName, indexReady):
        self.preprocessor = Preprocessor()
        
        # Determines which function to use to build an index.
        if indexReady:
            builder = self.loadIndex
        else:
            builder = self.buildIndex
        
        # Populates docNos and index field of the object.
        builder(fileName)
            
    # Loads index from ready .txt file. Populates the docNos and index fields of the SearchEngine
    # object. Assumes that inverted indexes for two terms in the file .txt file are separated 
    # by a newline.
    def loadIndex(self, fileName):
        self.index  = []
        self.docNos = set()
    
        with open(fileName, 'r') as file:
            idxTxt = ''
            
            for line in file:

                # Assumes that inverted indexes for two terms in the file .txt file are separated 
                # by a newline.
                if line == '\n':
                    termIndex   = TermIndex().fromString(idxTxt)
                    idxTxt      = ''
                    self.docNos = self.docNos.union(set(list(termIndex.termFreqs.keys())))
                    
                    self.index.append(termIndex)
                else:
                    idxTxt += line
        
        self.docNos = list(self.docNos)
        
        self.docNos.sort()

    def loadJSON(self, fileName):
        with open(fileName, 'r') as file:
            songs = loads([line for line in file][0])

            file.close()

        self.docNos = list(songs.keys())
        texts       = [song['lyrics'] for song in songs.values()]

        return texts
    
    # Takes the name of json file - fileName and extract lyrics from such file. The json file should 
    # hold a dictionary of songs in which each song ID is mapped to a song object. The function 
    # builds an index from such file and saves it in the index.txt file. Populates the index and 
    # docNos fields of the SearchEngine object.
    def buildIndex(self, fileName):
        self.index = []
        texts      = self.loadJSON(fileName)
        
        # Preprocess each document.
        texts = [self.preprocessor.preprocess(txt) for txt in texts]

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
        for word in lexicon:
            termIndex = TermIndex(word)

            for idx, text in enumerate(texts):

                # Checks if a word is in the lexicon of a given document - way faster than checking 
                # if word is in the entire text of the document.
                if word in sets[idx]:

                    # Compute number of time word occurs in a document with docNos[idx] id.
                    termFreq                              = sum([1 for term in text.split() if term == word])
                    termIndex.termFreqs[self.docNos[idx]] = termFreq

                    # word occurred in another document so increment its frequency.
                    termIndex.documentFreq = termIndex.documentFreq + 1

            self.index.append(termIndex)
        
        # Saves the built index into index.txt file in the format specified in the coursework 
        # document.
        self.saveIndex()
    
    # Saves inverted index into an index.txt file. Text representation of an inverted index for each 
    # term is separated by a newline from the inverted index of another term.
    def saveIndex(self):
        indexTxt = ''

        for termIndex in self.index:
            indexTxt += termIndex.toString() + '\n'

        with open('index.txt','w') as file:
            file.write(indexTxt) 
            file.close()
    
    # Performs ranked search for the query string. Outputs list of most relevant documents.
    def rankedSearch(self, query):

        # Preprocess the query
        query = self.preprocessor.preprocess(query)

        # Get dictionary in which each document id is mapped to its score for the query.
        scores = self.computeTFIDFs(query.split())

        # Sort the documents by their scores in descending order. Ensure that if two documents have 
        # the same score the one with lower document id occurs first in the output.
        scores       = OrderedDict(sorted(scores.items())[::-1])
        idx          = list(argsort(list(scores.values()), kind='stable'))[::-1]
        sortedDocs   = list(array(list(scores.keys()))[idx])

        return sortedDocs
    
    # Computes the TFIDF score for each document that contains one of the provided query terms.
    # Result is returned in a dictionary in which each document id is mapped to its score for the
    # query with specified terms. The terms should result from preprocessing the original query.
    def computeTFIDFs(self, terms):
        N      = len(self.docNos)
        scores = {}

        for termIndex in self.index:
            if termIndex.term in terms:
                idf = log10(N / termIndex.documentFreq)

                # Iterate over documents that contain the word.
                for docId in termIndex.termFreqs:
                    tf     = 1 + log10(termIndex.termFreqs[docId])
                    weight = tf * idf

                    if docId not in scores:
                        scores[docId] = 0
                        
                    scores[docId] = scores[docId] + weight

        return scores

    