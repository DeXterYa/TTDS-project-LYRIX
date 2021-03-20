from flask import render_template, url_for, flash, redirect, request
from lyrix import app, sp, preprocessor, songs_collection, index_collection, date_collection, session, artist_collection
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
	start_time = time.time()

	form = SearchBox()
	if form.validate_on_submit():
		flask.session['is_search'] = True
		return redirect(url_for('home', lyrics=form.lyrics.data, singer=form.singer.data,
		 startdate=form.year_begin.data, enddate=form.year_end.data, language=form.language.data))

	# acquire these queries after searching to keep them in the search box
	lyrics = request.args.get('lyrics', None)
	singer = request.args.get('singer', None)
	startdate = request.args.get('startdate', None)
	enddate = request.args.get('enddate', None)
	language = request.args.get('language', None)
	page_num = request.args.get('page_num', None)
	total_pages = request.args.get('total_pages', None)
	

	# Style attributes for the lanuguage drop-down menu
	attrs = {'class': "btn btn-outline-secondary dropdown-toggle", 'data-bs-toggle': "dropdown", 'aria-expanded': "false"}
	
	
	# check if the advanced search is used
	is_advanced = False
	advanced_dict = {}

	if (bool(singer) or bool(startdate) or bool(enddate)):
		# advanced search mode
		is_advanced = True
		advanced_dict = {"singer": singer, "startdate": startdate, "enddate":enddate}



	# initialize variables in case of no search
	displayed_page_links = 7
	page_list = []
	songs_per_page = 10
	
	relevance = []
	songs = []
	
	# retrieve songs (a list data structure)
	if lyrics and flask.session['is_search']:
		form.language.default = language
		form.process()
		results, scores, num_songs_retrieved = ranked_search(lyrics, preprocessor, songs_collection,
		  index_collection, artist_collection, date_collection, is_advanced, advanced_dict, language)
		flask.session['results'] = results
		flask.session['scores'] = scores

		# set number of pages based on number of retrieved songs
		total_pages = math.ceil(num_songs_retrieved / songs_per_page)
		page_num = 1


		# generate page list
		if total_pages >= displayed_page_links:
			page_list = [x for x in range(1, displayed_page_links + 1)]
		else:
			page_list = [x for x in range(1, total_pages + 1)]

		for song_id in results[songs_per_page*(page_num-1): songs_per_page*page_num]:
			for song in songs_collection.find({'_id': int(song_id)}):
				songs += [song]
				relevance += ["{:.2f}".format(scores[song_id])]

	elif lyrics:

		total_pages = int(total_pages)
		page_num = int(page_num)
		if total_pages >= displayed_page_links:
			if displayed_page_links % 2 == 1:
				if page_num <= displayed_page_links // 2:
					page_list = [x for x in range(1, displayed_page_links + 1)]
				elif page_num > total_pages - displayed_page_links // 2:
					page_list = [x for x in range(total_pages - displayed_page_links + 1, total_pages + 1)]
				else:
					page_list = [x for x in range(page_num - displayed_page_links // 2, page_num + displayed_page_links //2 + 1)]
			else:
				if page_num <= displayed_page_links // 2:
					page_list = [x for x in range(1, displayed_page_links + 1)]
				elif page_num > total_pages - displayed_page_links // 2:
					page_list = [x for x in range(total_pages - displayed_page_links + 1, total_pages + 1)]
				else:
					page_list = [x for x in range(page_num - displayed_page_links // 2, page_num + displayed_page_links //2)]
		else:
			page_list = [x for x in range(1, total_pages + 1)]



		for song_id in flask.session['results'][songs_per_page*(page_num-1): songs_per_page*page_num]:
			for song in songs_collection.find({'_id': int(song_id)}):
				songs += [song]
				relevance += ["{:.2f}".format(flask.session['scores'][song_id])]
	else:
		songs = None


	

	elapsed_time = time.time() - start_time

	# green flash message on top of the search box
	if 'is_search' in flask.session and lyrics and flask.session['is_search']:
		# no songs retireved
		if num_songs_retrieved == 0:
			flash(f'No results found ({elapsed_time:.6f}s)', 'danger')
		elif len(lyrics) <= 30:
			flash(f'{num_songs_retrieved} results found "{lyrics}" ({elapsed_time:.6f}s)', 'success')
		else:
			flash(f'{num_songs_retrieved} results found "{lyrics[:30]}..." ({elapsed_time:.6f}s)', 'success')
		flask.session['is_search'] = False

	if 'history' not in flask.session:
			flask.session['history'] = []


	return render_template('home.html', form=form, songs=songs, lyrics=lyrics, singer=singer,
	 						startdate=startdate, enddate=enddate, page_num=page_num, total_pages=total_pages,
							 songs_per_page=songs_per_page, relevance=relevance, attrs=attrs, history=flask.session['history'],
							 onHomePage=True, page_list=page_list)


@app.route('/about') # the about page of the website
def about():
	if 'history' not in flask.session:
			flask.session['history'] = []
	return render_template('about.html', title='About', 
		history=flask.session['history'], onHomePage=False)


@app.route('/lyrics', methods=['GET', 'POST']) 
def lyrics():

	song_id = request.args.get('song_id', None)
	relevance = request.args.get('relevance', None)

	if song_id:

		song = songs_collection.find({'_id': int(song_id)})[0]

		# record the song history of the user
		if 'history' not in flask.session:
			flask.session['history'] = [[song['title'], song_id, relevance]]
		else:
			if len(flask.session['history']) == 0:
				flask.session['history'].append([song['title'], song_id, relevance])
			elif len(flask.session['history']) >= 1:
				if len(flask.session['history'][0]) == 3 and flask.session['history'][0][1] != song_id:
					flask.session['history'].insert(0, [song['title'], song_id, relevance])
					if len(flask.session['history']) > 5:
						flask.session['history'].pop()
			print(flask.session['history'])
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


