from lyrix import app

# pip install Flask

# option 1:
# export FLASK_APP=lyrix.py
# export FLASK_DEBUG=1 (allow the website to show instant changes)
# flask run

# option 2:
# python lyrix.py

# create an instance of Flask class
# __name__ allows flask to know your templates and static files




# it is only true when running this script directly
if __name__ == '__main__':
    app.run(debug=True)