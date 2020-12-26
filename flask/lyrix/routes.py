from flask import render_template
from lyrix import app

# different pages
@app.route('/') # the root page of the website
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about') # the root page of the website
def about():
    return render_template('about.html', title='About')
