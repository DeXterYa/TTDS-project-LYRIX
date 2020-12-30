# TTDS 20-21 LYRIX: Lyrics Search Engine

Structure of this project:

```
.
├── flask
│   ├── lyrix
│   │   ├── forms.py
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
`./flask/lyrix/routes.py` contains all the routes in the application. `./flask/lyrix/models.py` contains fields for database.

In this branch,
* I used [Flask-MongoEngine](http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/) to connect the application 
  with a MongoDB database with 10 songs (used as dummy data) from Taylor Swift. 
* The application now keeps the search query on the web page after clicking the search button.
* The application now supports pagination of the search results.

## MongoDB
There are two ways of hosting the database. The first one is to host the database on the [cloud](https://www.mongodb.com/), 
which provides a free version with limited storage. After creating a database, you will get a connection string which allows 
you to connect to the database (I am using MongoDB Compass). Then you can upload your data to the database. With the help 
of Flask-MongoEngine, you can connect to your database through:

```python
 app.config['MONGODB_SETTINGS'] = {
    # my connection string, including my username (lyrix), password (123456QWEASDZXC) and database name (test)
 	'host': 'mongodb+srv://lyrix:123456QWEASDZXC@cluster0.2fg4d.mongodb.net/test',
 }
```
To connect with this database, it seems you have to specify your IP address in the server to allow the access. Because the 
database is not hosted locally, it takes a while to refresh the page.

The second option is to host the database on your local machine. To do this, you have to download the MongoDB to your local machine.
I used this [link](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/) for my Ubuntu machine. Following
the instructions on the link, I executed:

```
$ sudo systemctl start mongod
$ sudo systemctl status mongod
```
However, I found out that my MongoDB was not running. With the help of this [link](https://stackoverflow.com/questions/37565758/mongodb-not-working-on-ubuntu-16-04/42736439)
, I ran the commands:
```
$ sudo chown mongodb /tmp/mongodb-27017.sock
$ sudo chgrp mongodb /tmp/mongodb-27017.sock
```
and solved the problem.

In a similar vein, you can upload your data (.csv or .json) to the database and connect your flask application with MongoDB:
```python
app.config['MONGODB_SETTINGS'] = {
    'db': 'test',
    'host': 'localhost',
    'port': 27017
}
```
(Assuming that we use the same host and port)