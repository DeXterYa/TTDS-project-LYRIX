from flask import render_template, url_for, flash, redirect, request
from lyrix import app, sp, preprocessor, songs_collection, index_collection, is_search, session
from lyrix.query import ranked_search
from lyrix.forms import SearchBox
import flask
import time
import math
from itertools import groupby  


# different pages
@app.route('/', methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
	global is_search
	form = SearchBox()
	if form.validate_on_submit():
		is_search = True
		flask.session['is_search'] = True
		return redirect(url_for('home', lyrics=form.lyrics.data, singer=form.singer.data,
		 startdate=form.year_begin.data, enddate=form.year_end.data, language=form.language.data))

	# acquire these queries after searching to keep them in the search box
	lyrics = request.args.get('lyrics', None)
	singer = request.args.get('singer', None)
	startdate = request.args.get('startdate', None)
	enddate = request.args.get('enddate', None)
	language = request.args.get('language', None)
	attrs = {'class': "btn btn-outline-secondary dropdown-toggle", 'data-bs-toggle': "dropdown", 'aria-expanded': "false"}
	
	
	is_advanced = False
	advanced_dict = {}

	
	if (singer or startdate or enddate):
		# advanced search mode
		is_advanced = True
		advanced_dict = {"singer": singer, "startdate": startdate, "enddate":enddate}



	# number of songs retrieved for a query
	max_num_songs_retrieved = 40

	start_time = time.time()

	# initialize variables in case of no search
	songs_per_page = 10
	num_songs_retrieved = 0
	num_pages = 0
	relevance = []

	
	# retrieve songs (a list data structure)
	if lyrics:
		form.language.default = language
		form.process()
		songs, relevance = ranked_search(lyrics, preprocessor, songs_collection,
		  index_collection, max_num_songs_retrieved, is_advanced, advanced_dict, language)

		# set number of pages based on number of retrieved songs
		num_songs_retrieved = len(songs)
		num_pages = math.ceil(num_songs_retrieved / songs_per_page)
	else:
		songs = None


	elapsed_time = time.time() - start_time

	# green flash message on top of the search box
	if 'is_search' in flask.session and lyrics and flask.session['is_search']:
		# no songs retireved
		if num_songs_retrieved == 0:
			flash(f'No results found ({elapsed_time:.6f}s)', 'danger')
		elif len(lyrics) <= 44:
			flash(f'Results found "{lyrics}" ({elapsed_time:.6f}s)', 'success')
		else:
			flash(f'Results found "{lyrics[:44]}..." ({elapsed_time:.6f}s)', 'success')
		flask.session['is_search'] = False

	if 'history' not in flask.session:
			flask.session['history'] = [[]]


	return render_template('home.html', form=form, songs=songs, lyrics=lyrics, singer=singer,
	 						startdate=startdate, enddate=enddate, num_songs_retrieved=num_songs_retrieved, num_pages=num_pages,
							 songs_per_page=songs_per_page, relevance=relevance, attrs=attrs, history=flask.session['history'],
							 onHomePage=True)


@app.route('/about') # the about page of the website
def about():
	if 'history' not in flask.session:
			flask.session['history'] = [[]]
	return render_template('about.html', title='About', 
		history=flask.session['history'], onHomePage=False)


@app.route('/lyrics', methods=['GET', 'POST']) 
def lyrics():

	song_id = request.args.get('song_id', None)
	relevance = request.args.get('relevance', None)

	if song_id:


		song = songs_collection.find({'_id': int(song_id)})[0]
		if 'history' not in flask.session:
			flask.session['history'] = [[song_id, song.title, relevance]]
		else:
			if len(flask.session['history']) >= 1:
				if len(flask.session['history'][0]) == 3 and flask.session['history'][0][1] != song_id:
					flask.session['history'].insert(0, [song['title'], song_id, relevance])
					if len(flask.session['history']) > 5:
						flask.session['history'].pop()


	else:
		song = None

	query = '"' + song['title'] +'"' + ' artist:"' + song['author'][0] + '"'
	token, img_url = "", ""
	sp_result = sp.search(q=query, limit=1)
	for idx, track in enumerate(sp_result['tracks']['items']):
		token = "https://open.spotify.com/embed/track/" + track['external_urls']['spotify'].rsplit('/', 1)[-1]
		img_url = track['album']['images'][0]['url']

	return render_template('lyrics.html', song=song, token=token, 
		img_url=img_url, relevance=relevance, history=flask.session['history'], onHomePage=False)


