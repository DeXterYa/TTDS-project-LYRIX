# TTDS 20-21 LYRIX: Lyrics Search Engine

Structure of this project:

```
.
├── flask
│   ├── lyrix
│   │   ├── forms.py
│   │   ├── __init__.py
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
`./flask/lyrix/routes.py` contains all the routes in the application.