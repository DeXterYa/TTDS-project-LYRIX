from lyrix import db

class Lyrics(db.Document):
	# connect with a specific collection in the database
	meta = {'collection':'lyrics_group1'}
	# a list of fields
	index = db.StringField()
	artist = db.StringField()
	song = db.StringField()
	lyrics = db.StringField()

