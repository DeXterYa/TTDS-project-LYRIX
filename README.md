# TTDS 20-21 LYRIX: Lyrics Search Engine

Structure of this project:

```
.
├── flask
│   ├── lyrix
│   │   ├── forms.py
│   │   ├── index.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── static
│   │   │   ├── main.css
│   │   │   └── profile_pics
│   │   │       ├── dexter.jpg
│   │   │       ├── maciej.jpg
│   │   │       ├── marcin.jpg
│   │   │       └── matus.jpg
│   │   └── templates
│   │       ├── about.html
│   │       ├── home.html
│   │       └── layout.html
│   └── run.py
├── README.md
└── requirements.txt

```

In the `./flask/`, we adopted a package structure.

To run this application,

```
$ pip install -r requirements.txt
$ cd flask
$ python run.py
```
`./flask/lyrix/` contains all the other files. `./flask/lyrix/static/` contains a css file and profile pics for team members. `./flask/lyrix/templates/` contains all the html files.
(`layout.html` is the shared layout for all other html files) `./flask/lyrix/forms.py` contains search fields (a form) in the home page. 
`./flask/lyrix/routes.py` contains all the routes in the application. `./flask/lyrix/models.py` contains fields for database. `./flask/lyrix/index.py` is an API for ranking search results.

In this branch,
* I used [Flask-MongoEngine](http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/) to connect the application 
  with a MongoDB database with genius lyrics data. 
  
* Added index.py to the application. genius_index.json is stored outside this directory because of its size.
* Database name: lyrix; Collection name: genius.
* Return elapsed time 
* Added an icon for the tab in browsers


