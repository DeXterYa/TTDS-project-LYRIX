from flask import render_template, url_for, flash, redirect, request
from lyrix import app, se, sp
from lyrix.forms import SearchBox
from lyrix.models import Lyrics
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

	# acquire current page of the search results
	page = request.args.get('page', 1, type=int)
	
	num_idx = 40
	per_page = 4
	num_pages = math.ceil(num_idx / per_page)

	if page != num_pages:
		start_idx = (page - 1) * per_page
		end_idx = page * per_page
	else:
		start_idx = (page - 1) * per_page
		end_idx = num_idx

	page_list = [i  if i==1 or i==page-1 or i==page or i==page+1 or i==page+2 or i==num_pages else 0 for i in range(1, num_pages + 1)]
	page_list = [i[0] for i in groupby(page_list)]
	start_time = time.time()
	if lyrics:
		ids = se.rankedSearch(lyrics)[:num_idx]

		stack = [];
		for i in range(len(ids)-1, 0, -1):
		    rec = {
		        "$cond": [
		            {"$eq": ["$id", ids[i-1]]}, i
		        ]
		    }
		    if len(stack) == 0:
		        rec["$cond"].append(i+1)
		    else:
		        lval = stack.pop()
		        rec["$cond"].append(lval)
		    
		    stack.append(rec)

		pipeline = [
		    { "$match": {
		        "id": { "$in": ids }}
		    },
		    { "$addFields": {
		        "weight": stack[0]
		    }},
		    {"$sort" : {"weight" : 1}}]
		songs = Lyrics.objects().aggregate(pipeline)
		
		
	else:
		songs = None

	elapsed_time = time.time() - start_time

	form = SearchBox()
	# green flash message on top of the search box
	if form.validate_on_submit():
		flash(f'Results found {form.lyrics.data}{form.singer.data}{form.year_begin.data}{form.year_end.data}! ({elapsed_time:.6f}s)', 'success')
		
		return redirect(url_for('home', lyrics=form.lyrics.data, singer=form.singer.data, startdate=form.year_begin.data, enddate=form.year_end.data))

	return render_template('home.html', form=form, songs=songs, lyrics=lyrics, singer=singer,
	 						startdate=startdate, enddate=enddate, page=page, page_list=page_list,
	 						start_idx=start_idx, end_idx=end_idx)


@app.route('/about') # the about page of the website
def about():
    return render_template('about.html', title='About')


@app.route('/lyrics', methods=['GET', 'POST']) 
def lyrics():

	song_id = request.args.get('song_id', None)

	if song_id:
		song = Lyrics.objects(id=song_id)[0]

	query = '"' + song.title +'"' + ' artist:"' + song.author[0] + '"'
	
	sp_result = sp.search(q=query, limit=1)
	for idx, track in enumerate(sp_result['tracks']['items']):
		token = "https://open.spotify.com/embed/track/" + track['external_urls']['spotify'].rsplit('/', 1)[-1]
		img_url = track['album']['images'][0]['url']

	return render_template('lyrics.html', song=song, token=token, img_url=img_url)


