from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

# search box for the home page including the advanced search
class SearchBox(FlaskForm):

	choices = [('da', 'Danish'),
                    ('nl', 'Dutch'), 
                    ('en', 'English'),
                    ('fi', 'Finnish'),
                    ('fr', 'French'),
                    ('de', 'German'),
                    ('hu', 'Hungarian'),
                    ('it', 'Italian'),
                    ('no', 'Norwegian'),
                    ('pt', 'Portuguese'),
                    ('ro', 'Romanian'),
                    ('es', 'Spanish'),
                    ('sv', 'Swedish')]
                    
	lyrics = StringField('Search Lyrics', validators=[DataRequired()])
	language = SelectField('Language', choices=choices, default='en')
	singer = StringField('Singer')
	year_begin = StringField('Begin')
	year_end = StringField('End')
	submit = SubmitField('Search')