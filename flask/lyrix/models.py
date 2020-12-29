from lyrix import db

class Lyrics(db.Document):
	meta = {'collection':'lyrics_group1'}
	index = db.StringField()
	artist = db.StringField()
	song = db.StringField()
	lyrics = db.StringField()

