from flask import render_template, url_for, flash, redirect, request
from lyrix import app
from lyrix.forms import SearchBox
from lyrix.models import Lyrics

# different pages
# @app.route('/<string:lyrics>/<string:singer>/<string:startdate>/<string:enddate>', methods=['GET', 'POST']) # the root page of the website
@app.route('/', methods=['GET', 'POST'])
def home():
	lyrics = request.args.get('lyrics', None)
	singer = request.args.get('singer', None)
	startdate = request.args.get('startdate', None)
	enddate = request.args.get('enddate', None)

	songs = Lyrics.objects(artist="Taylor Swift")
	form = SearchBox()
	# green flash message on top of the search box
	if form.validate_on_submit():
		flash(f'Results found {form.lyrics.data}{form.singer.data}{form.year_begin.data}{form.year_end.data}!', 'success')
		
		return redirect(url_for('home', lyrics=form.lyrics.data, singer=form.singer.data, startdate=form.year_begin.data, enddate=form.year_end.data))

	return render_template('home.html', form=form, songs=songs, lyrics=lyrics, singer=singer, startdate=startdate, enddate=enddate)

@app.route('/about') # the about page of the website
def about():
    return render_template('about.html', title='About')

