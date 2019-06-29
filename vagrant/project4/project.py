from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Game, User

from flask import session as login_session
import random, string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Game Catalog"

#Establish connection to the gameCatalog db
engine = create_engine('sqlite:///gameCatalog.db', 
            connect_args={'check_same_thread': False})

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session = DBSession()

@app.route('/loggingIn')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)    

#Home page that lists genres
@app.route('/')
@app.route('/home/')
def genreSelectMenu():
    genres = session.query(Genre).all()
    return render_template('home.html', genres=genres)

#Genre page that displays the selected genre
@app.route('/<int:genre_id>', methods=['GET'])
def exploreGenre(genre_id):
    selectedGenre = session.query(Genre).filter_by(id=genre_id).first()
    gamesInGenre = session.query(Game).filter_by(genreID=selectedGenre.id)
    return render_template('genreExplorer.html', 
                            gamesInGenre=gamesInGenre, 
                            selectedGenre=selectedGenre)

#Game page displays selected games information
@app.route('/<int:game_id>/view', methods=['GET'])
def viewGameDetails(game_id):
    currentUser = login_session['username']
    selectedGame = session.query(Game).filter_by(id=game_id).first()
    return render_template('viewGame.html',
                            selectedGame = selectedGame,
                            currentUser = currentUser)

@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    #if 'username' not in login_session:
        #return redirect('/loggingIn')
    if request.method == 'POST':
      newGenre = Genre(name = request.form['name'])
      session.add(newGenre)
      flash('New Genre %s Successfully Created' % newGenre.name)
      session.commit()
      return redirect(url_for('genreSelectMenu'))
    else:
      return render_template('newGenre.html')

@app.route('/<int:game_id>/edit', methods=['GET', 'POST'])
def editGameDetails(game_id):
    editedGame = session.query(Game).filter_by(id=game_id).first()
    if request.method=='POST':
        editedGame.name = request.form['name']
        editedGame.esrb = request.form['esrb']
        editedGame.releaseYear = request.form['releaseYear']
        editedGame.platforms = request.form['platforms']
        editedGame.desc = request.form['desc']
        session.add(editedGame)
        session.commit()
        return redirect(url_for('exploreGenre', genre_id = editedGame.genreID))
    else:
        return render_template('editGameDetails.html', editedGame=editedGame)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if user_id == None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None 

if __name__ == '__main__':
    app.secret_key = 'SeCrEtKeY'
    app.debug = False
    app.run(host='0.0.0.0', port=5000)