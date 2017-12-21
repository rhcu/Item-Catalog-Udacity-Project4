from flask import Flask, render_template, request
from flask import redirect,  url_for, jsonify, flash, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import User, Base, Genre, BookItem
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import GoogleCredentials
import random
import string
import httplib2
import requests
import json
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "BookShelf"

engine = create_engine('sqlite:///new_book_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('genres.html', STATE=state)


@app.route('/gconnect', methods=['POST', 'GET'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid State Parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("Failed to upgrade auth code"),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps('error'), 500)
        response.headers['Content-Type'] = 'application/json'
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Users ids do not match"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token id does not match app id"),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("User already connected"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '</h1>'
    return output


@app.route('/gdisconnect/')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps("User is not connected"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result['status']
    if result['status'] == '400':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        response = make_response(json.dumps("You are disconnected"), 200)
        flash('You are disconnected')
        response.headers['Content-Type'] = 'application/json'
        return redirect('/genres')
    else:
        response = make_response(json.dumps("Error occured"), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# User related functions for local permission system
# Creates and adds a user to the database, returning his id
def createUser(login_session):
    user = User(name=login_session['username'], 
                email=login_session['email'],
                picture=login_session['picture'])
    session.add(user)
    session.commit()
    user_db = session.query(User).filter_by(email=login_session['email']).one()
    return user_db.id


# Searches information related to the user, user_id is given as argument
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Searches user_id based on user email. None if not found
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# show all available genres
@app.route('/')
@app.route('/genres/')
def showGenres():
    genres = session.query(Genre).all()
    if 'username' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
        return render_template('public_genres.html', genres=genres, STATE=state)
    else:
        return render_template('genres.html', genres=genres)


# show the list of books for one genre
@app.route('/genres/<int:genre_id>/')
@app.route('/genres/<int:genre_id>/books/')
def showBooks(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    books = session.query(BookItem).filter_by(genre_id=genre_id).all()
    if 'username' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
        return render_template('public_books.html', genre=genre, books=books, STATE=state)
    return render_template('books.html', books=books, genre=genre)


# add a new genre
@app.route('/genres/new/', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGenre = Genre(name=request.form['name'],
                         description=request.form['description'], 
                         user_id=login_session['user_id'])
        session.add(newGenre)
        session.commit()
        flash('Genre was successfully added to the catalog')
        return redirect(url_for('showGenres'))
    else:
        return render_template('newGenre.html')


# add a new book for a genre
@app.route('/genres/<int:genre_id>/books/new/',  methods=['GET', 'POST'])
def newBook(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBook = BookItem(name=request.form['name'],
                           author=request.form['author'], 
                           description=request.form['description'], 
                           price=request.form['price'], type=request.form['type'],
                           user_id=login_session['user_id'], genre_id=genre_id)
        session.add(newBook)
        session.commit()
        flash('Book was successfully added to the list')
        return redirect(url_for('showBooks', genre_id=genre_id))
    else:
        return render_template('newBook.html', genre_id=genre_id)


# edit a genre
@app.route('/genres/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genreToEdit = session.query(Genre).filter_by(id=genre_id).one()
    if genreToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('No access');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            genreToEdit.name = request.form['name']
        if request.form['description']:
            genreToEdit.description = request.form['description']
        session.add(genreToEdit)
        session.commit()
        flash('Genre %s was successfully edited' % genreToEdit.name)
        return redirect(url_for('showGenres'))
    else:
        return render_template('editGenre.html', genre=genreToEdit)


# edit a book
@app.route('/genres/<int:genre_id>/books/<int:book_id>/edit/', methods=['GET', 'POST'])
def editBook(genre_id, book_id):
    print login_session
    if 'username' not in login_session:
        return redirect('/login')
    bookToEdit = session.query(BookItem).filter_by(id=book_id).one()
    if request.method == 'POST':
        if request.form['name']:
            bookToEdit.name = request.form['name']
        if request.form['description']:
            bookToEdit.description = request.form['description']
        if request.form['price']:
            bookToEdit.price = request.form['price']
        if request.form['type']:
            bookToEdit.type = request.form['type']
        if request.form['author']:
            bookToEdit.author = request.form['author']
        bookToEdit.id = book_id
        bookToEdit.genre_id = genre_id
        session.add(bookToEdit)
        session.commit()
        flash('Book %s was successfully edited' % bookToEdit.name)
        return redirect(url_for('showBooks', genre_id=genre_id))
    else:
        return render_template(
                                'editBook.html', genre_id=genre_id, book_id=book_id, book=bookToEdit)


# delete a genre
@app.route('/genres/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genreToDelete = session.query(Restaurant).filter_by(id=genre_id).one()
    if genreToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('No access');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(genreToDelete)
        session.commit()
        flash('Genre was successfully deleted from the catalog')
        return redirect(url_for('showGenres', genre_id=genre_id))
    else:
        return render_template('deleteGenre.html', genre=genreToDelete)


# delete a book 
@app.route('/genres/<int:genre_id>/books/<int:book_id>/delete/',  methods=['GET', 'POST'])
def deleteBook(genre_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    bookToDelete = session.query(BookItem).filter_by(id=book_id).one()
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash('Book was successfully deleted from the list')
        return redirect(url_for('showBooks', genre_id=genre_id))
    else:
        return render_template('deleteBook.html', book=bookToDelete)


# JSON API endpoints
@app.route('/genres/JSON/')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(genres=[g.serialize for g in genres])


@app.route('/genres/<int:genre_id>/books/JSON/')
def showBooksJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    books = session.query(BookItem).filter_by(genre_id=genre_id).all()
    return jsonify(books=[b.serialize for b in books])


@app.route('/genres/<int:genre_id>/books/<int:book_id>/JSON/')
def showBookItemJSON(genre_id, book_id):
    Book_Item = session.query(BookItem).filter_by(id=book_id).one()
    return jsonify(Book_Item=Book_Item.serialize)


if __name__ == '__main__':
    app.secret_key = 'some_very_difficult_key_to_protect_data'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
