from flask import render_template, url_for, flash, redirect
from lyrix import app
from lyrix.forms import SearchBox
from lyrix.models import Lyrics

# different pages
@app.route('/', methods=['GET', 'POST']) # the root page of the website
@app.route('/home', methods=['GET', 'POST'])
def home():
	songs = Lyrics.objects(artist="Taylor Swift")
	form = SearchBox()
	# green flash message on top of the search box
	if form.validate_on_submit():
		flash(f'Results found {form.lyrics.data}!', 'success')
		return redirect(url_for('home'))

	return render_template('home.html', form=form, songs=songs)

@app.route('/about') # the about page of the website
def about():
    return render_template('about.html', title='About')

