from flask import Flask
from flask_mongoengine import MongoEngine
from lyrix.index import SearchEngine
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
# secret key for wtforms
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

# Option 1: host the database on a MongoDB server. It requires special access
# app.config['MONGODB_SETTINGS'] = {
# 	'host': 'mongodb+srv://lyrix:123456QWEASDZXC@cluster0.2fg4d.mongodb.net/test',
# }


# Option 2: host the databse on your local machine
app.config['MONGODB_SETTINGS'] = {
	'db': 'lyrix',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine(app)

se = SearchEngine()
se.loadIndex(fileName='../../index/genius_index.json')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="e03291f52cfb40c284711b9e6459b14d",
                                                           client_secret="929ee5a32b5140b19c97358fc70fb655"))


from lyrix import routes
