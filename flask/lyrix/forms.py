from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# search box for the home page including the advanced search
class SearchBox(FlaskForm):
	lyrics = StringField('Search Lyrics', validators=[DataRequired()])
	singer = StringField('Singer')
	year_begin = StringField('Begin')
	year_end = StringField('End')
	submit = SubmitField('Search')