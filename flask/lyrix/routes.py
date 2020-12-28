from flask import render_template, url_for, flash, redirect
from lyrix import app
from lyrix.forms import SearchBox

# different pages
@app.route('/', methods=['GET', 'POST']) # the root page of the website
@app.route('/home', methods=['GET', 'POST'])
def home():
	form = SearchBox()
	if form.validate_on_submit():
		flash(f'Results found {form.lyrics.data}!', 'success')
		return redirect(url_for('home'))
	return render_template('home.html', form=form)

@app.route('/about') # the root page of the website
def about():
    return render_template('about.html', title='About')


@app.route('/test') # the root page of the website
def test():
    return render_template('test.html')