from flask import render_template, url_for, flash, redirect, request
from lyrix import app, sp, preprocessor, songs_collection, index_collection
from lyrix.query import ranked_search
from lyrix.forms import SearchBox

import time
import math
from itertools import groupby  

# different pages
@app.route('/', methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
	# acquire these queries after searching to keep them in the search box
	lyrics = request.args.get('lyrics', None)
	singer = request.args.get('singer', None)
	startdate = request.args.get('startdate', None)
	enddate = request.args.get('enddate', None)

	# number of songs retrieved for a query
	max_num_songs_retrieved = 40

	start_time = time.time()

	# retrieve songs (a list data structure)
	if lyrics:
		songs = ranked_search(lyrics, preprocessor, songs_collection, index_collection, max_num_songs_retrieved)
	else:
		songs = None

	if songs:
		num_songs_retrieved = len(songs)
	else:
		num_songs_retrieved = 0
	# number of songs per page
	songs_per_page = 5
	num_pages = math.ceil(num_songs_retrieved / songs_per_page)

	elapsed_time = time.time() - start_time

	form = SearchBox()
	# green flash message on top of the search box
	if form.validate_on_submit():
		flash(f'Results found {form.lyrics.data}{form.singer.data}{form.year_begin.data}{form.year_end.data}! ({elapsed_time:.6f}s)', 'success')
		
		return redirect(url_for('home', lyrics=form.lyrics.data, singer=form.singer.data, startdate=form.year_begin.data, enddate=form.year_end.data))

	return render_template('home.html', form=form, songs=songs, lyrics=lyrics, singer=singer,
	 						startdate=startdate, enddate=enddate, num_songs_retrieved=num_songs_retrieved, num_pages=num_pages,
							 songs_per_page=songs_per_page)


@app.route('/about') # the about page of the website
def about():
    return render_template('about.html', title='About')


@app.route('/lyrics', methods=['GET', 'POST']) 
def lyrics():

	song_id = request.args.get('song_id', None)

	if song_id:
		song = songs_collection.find({'_id': int(song_id)})[0]
	else:
		song = None

	query = '"' + song['title'] +'"' + ' artist:"' + song['author'][0] + '"'
	token, img_url = "", ""
	sp_result = sp.search(q=query, limit=1)
	for idx, track in enumerate(sp_result['tracks']['items']):
		token = "https://open.spotify.com/embed/track/" + track['external_urls']['spotify'].rsplit('/', 1)[-1]
		img_url = track['album']['images'][0]['url']

	return render_template('lyrics.html', song=song, token=token, img_url=img_url)


