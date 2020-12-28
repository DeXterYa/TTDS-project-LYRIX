from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchBox(FlaskForm):
	lyrics = StringField('Search Lyrics', validators=[DataRequired()])
	submit = SubmitField('Search')