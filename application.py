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

# CLIENT_ID for Google Signin
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "BookShelf"

# Database session setup
engine = create_engine('sqlite:///new_book_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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
        response = make_response(json.dumps('Failed to upgrade auth code'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # is access_token valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    # store the result of request
    result = json.loads(h.request(url, 'GET')[1])
    # if result contains any errors the message is sent to server
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # verify if this the right access_token
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps('Users ids do not match'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # is this token was issued for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps('Token id does not match app id'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # checks is the user already logged in not to reset all info
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    user_id = getUserID(data['email'])
    if not user_id:
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
    print access_token
    if access_token is None:
        response = make_response(json.dumps('User is not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        response = make_response(json.dumps("You are disconnected"), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/genres')
    else:
        response = make_response(json.dumps("Error occured"), 400)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/genres')


# User related functions for local permission system

def createUser(login_session):
    """
    createUser(login_session): creates a user
                               with given credentials
    Args:
        login_session(data-type: session) has info about
                                          the current logged user
    Returns:
        user id from database
    """
    user = User(name=login_session['username'],
                email=login_session['email'],
                picture=login_session['picture'])
    session.add(user)
    session.commit()
    user_db = session.query(User).filter_by(email=login_session['email']).one()
    return user_db.id


def getUserInfo(user_id):
    """
    getUserInfo(user_id): searches user-info by his id
    Args:
        user_id(data-type: int) a unique value
        that identifies a user in DB
    Returns:
        user info (username, email, picture)
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    getUserID(email): searches a user by his email
    Args:
        email(data-type: string) a unique value
        that identifies a user in DB
    Returns:
        user.id or None if no such email in DB
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/')
@app.route('/genres/')
def showGenres():
    """
    showGenres(): shows a list of genres
    Args:
        None
    Returns:
        renders a template with a list of genres
    """
    genres = session.query(Genre).all()
    if 'username' not in login_session:
        return render_template('public_genres.html', genres=genres)
    else:
        return render_template('genres.html', genres=genres,
                               user=login_session['email'],
                               picture=login_session['picture'])


@app.route('/genres/<int:genre_id>/')
@app.route('/genres/<int:genre_id>/books/')
def showBooks(genre_id):
    """
    showBooks(): shows a list of books of a specific genre
    Args:
        genre_id (data-type: int) primary key of Genre class
    Returns:
        renders a template with a list of books of the genre
    """
    genre = session.query(Genre).filter_by(id=genre_id).one_or_none()
    if genre is None:
        return "No such element"
    books = session.query(BookItem).filter_by(genre_id=genre_id).all()
    if 'username' not in login_session:
        return render_template('public_books.html', genre=genre, books=books)
    return render_template('books.html', books=books,
                           genre=genre, user=login_session['email'])


@app.route('/genres/new/', methods=['GET', 'POST'])
def newGenre():
    """
    newGenre(): creates a Genre
    Args:
        None
    Returns:
        redirects to the method that shows the
        list of genres
    """
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


@app.route('/genres/<int:genre_id>/books/new/',
           methods=['GET', 'POST'])
def newBook(genre_id):
    """
    newBook(genre_id): adds a BookItem to Genre
    Args:
        genre_id (data type: int): primary key of Genre class
    Returns:
        redirects to the method that shows the
        list of books of genre if successful
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if 'type' not in request.form:
            type = 'eBook'
        else:
            type = request.form['type']
        newBook = BookItem(name=request.form['name'],
                           author=request.form['author'],
                           description=request.form['description'],
                           price=request.form['price'],
                           user_id=login_session['user_id'], genre_id=genre_id)
        session.add(newBook)
        session.commit()
        flash('Book was successfully added to the list')
        return redirect(url_for('showBooks', genre_id=genre_id))
    else:
        return render_template('newBook.html', genre_id=genre_id)


@app.route('/genres/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    """
    editGenre(genre_id): edits a genre
    Args:
        genre_id (data type: int): primary key of Genre class
    Returns:
        redirects to the method that shows the
        list of genres if successful
    """
    if 'username' not in login_session:
        return redirect('/login')
    genreToEdit = session.query(Genre).filter_by(id=genre_id).one_or_none()
    if genreToEdit is None:
        return ("<script>function myFunction() {alert('No such element');"
                "window.history.back();}</script>"
                "<body onload='myFunction()''>")
    if genreToEdit.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('No access');"
                "window.history.back();}</script>"
                "<body onload='myFunction()''>")
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


@app.route('/genres/<int:genre_id>/books/<int:book_id>/edit/',
           methods=['GET', 'POST'])
def editBook(genre_id, book_id):
    """
    editBook(genre_id, book_id): edits a BookItem
    Args:
        genre_id (data type: int): id of a genre book belongs to
        book_id (data type: int): primary key for a book
    Returns:
        redirects to the method that shows the list
        of books of the genre if successful
    """
    if 'username' not in login_session:
        return redirect('/login')
    bookToEdit = session.query(BookItem).filter_by(id=book_id).one_or_none()
    if bookToEdit is None:
        return ("<script>function myFunction() {alert('No such element');"
                "window.history.back();}</script>"
                "<body onload='myFunction()''>")
    if bookToEdit.user_id != login_session['user_id']:
        return ("<script>function myFunction()"
                "{alert('No access');window.history.back();}"
                "</script><body onload='myFunction()''>")
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
        return render_template('editBook.html', genre_id=genre_id,
                               book_id=book_id, book=bookToEdit)


@app.route('/genres/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    """
    deleteGenre(genre_id): deletes a Genre
    Args:
        genre_id (data type: int): primary key of genre
    Returns:
        redirects to the method that shows the
        list of genres if successful
    """
    if 'username' not in login_session:
        return redirect('/login')
    genreToDelete = session.query(Genre).filter_by(id=genre_id).one_or_none()
    if genreToDelete is None:
        return ("<script>function myFunction() {alert('No such element');"
                "window.history.back();}</script>"
                "<body onload='myFunction()''>")
    if genreToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction()"
                "{alert('No access');"
                "window.history.back();"
                "}</script><body onload='myFunction()''>")
    if request.method == 'POST':
        session.delete(genreToDelete)
        session.commit()
        flash('Genre was successfully deleted from the catalog')
        return redirect(url_for('showGenres', genre_id=genre_id))
    else:
        return render_template('deleteGenre.html', genre=genreToDelete)


@app.route('/genres/<int:genre_id>/books/<int:book_id>/delete/',
           methods=['GET', 'POST'])
def deleteBook(genre_id, book_id):
    """
    deleteBook(genre_id, book_id): deletes a BookItem
    Args:
        genre_id (data type: int): id of a genre book belongs to
        book_id (data type: int): primary key for a book
    Returns:
        redirects to the method that shows the
        list of books of genre if successful
    """
    if 'username' not in login_session:
        return redirect('/login')
    bookToDelete = session.query(BookItem).filter_by(id=book_id).one_or_none()
    if bookToDelete is None:
        return ("<script>function myFunction() {alert('No such element');"
                "window.history.back();"
                "window.history.back();}</script>"
                "<body onload='myFunction()''>")
    if bookToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction()"
                "{alert('No access');}</script><body onload='myFunction()''>")
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
    genre = session.query(Genre).filter_by(id=genre_id).one_or_none()
    if genre is None:
        return "No such element."
    books = session.query(BookItem).filter_by(genre_id=genre_id).all()
    return jsonify(books=[b.serialize for b in books])


@app.route('/genres/<int:genre_id>/books/<int:book_id>/JSON/')
def showBookItemJSON(genre_id, book_id):
    Book_Item = session.query(BookItem).filter_by(id=book_id).one_or_none()
    if Book_Item is None:
        return "No such element."
    return jsonify(Book_Item=Book_Item.serialize)


if __name__ == '__main__':
    app.secret_key = 'some_very_difficult_key_to_protect_data'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
