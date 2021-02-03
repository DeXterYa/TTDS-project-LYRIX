from lyrix import db

class Lyrics(db.Document):
	# connect with a specific collection in the database
	meta = {'collection':'genius', 'strict': False}
	# a list of fields
	id = db.StringField()
	author = db.ListField(db.StringField())
	title = db.StringField()
	lyrics = db.StringField()

