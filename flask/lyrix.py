from flask import Flask, render_template

# pip install Flask

# option 1:
# export FLASK_APP=lyrix.py
# export FLASK_DEBUG=1 (allow the website to show instant changes)
# flask run

# option 2:
# python lyrix.py

# create an instance of Flask class
# __name__ allows flask to know your templates and static files
app = Flask(__name__)


# different pages
@app.route('/') # the root page of the website
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about') # the root page of the website
def about():
    return render_template('about.html', title='About')

# it is only true when running this script directly
if __name__ == '__main__':
    app.run(debug=True)