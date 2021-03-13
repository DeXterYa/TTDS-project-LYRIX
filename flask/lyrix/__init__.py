from flask import Flask, session
from flask_session import Session
import pymongo
from lyrix.preprocessor import Preprocessor
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
# secret key for wtforms
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)


client           = pymongo.MongoClient("mongodb://localhost:27017/")
database         = client["lyrix"]
songs_collection = database["songs"]
index_collection = database["song_index"]
preprocessor = Preprocessor()

is_search = False


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="e03291f52cfb40c284711b9e6459b14d",
                                                           client_secret="929ee5a32b5140b19c97358fc70fb655"))


from lyrix import routes
