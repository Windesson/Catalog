from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import random, os, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import database_queries as q
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Silva's APP"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]


    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']

    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    flash('Successfully disconnected.')
    return redirect('/catalog')


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
        login_session['credentials'] = credentials
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = q.getUserID(data["email"])
    if not user_id:
        user_id = q.createUser(login_session)
    login_session['user_id'] = user_id

    print(login_session)
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
              150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


@app.route('/user/profile')
@login_required
def userProfile():
    user_id = login_session.get('user_id')
    items = q.get_menuitembyuserid(user_id)
    return render_template('userprofile.html', items = items, navuser="active")


@app.route('/')
@app.route('/catalog')
def catalogMenu():
    categories = q.get_catalog()
    items = q.get_latestitems()
    if items and categories:
        return render_template('index.html', categories = categories,
                            items = items, navhome = "active")
    else:
        return render_template('opps.html')


@app.route('/catalog/<category>/items')
def categoryItem(category):
    categories = q.get_catalog()
    items = q.get_menuitembycategoryname(category)
    if items and categories:
        return render_template('index.html', categories = categories,
                                items = items, categoryname = category )
    if categories:
        return render_template('index.html', categories = categories,
                                items = items, categoryname = category )
    else:
        return render_template('opps.html')


@app.route('/catalog/JSON')
def catalogJSON():
    return q.get_catalog_json()


@app.route('/catalog/<category>/<item>')
def categoryItemDetail(category,item):
    Item = q.get_menuitem(category,item)
    if Item:
        owner = (Item.user_id == login_session.get('user_id',False))
        return render_template('item.html', menuitem = Item, creator = owner,
                                category = category )
    else:
        return render_template('opps.html')


@app.route('/catalog/<category>/<item>/edit',methods=['GET','POST'])
@login_required
def editMenuItem(category,item):
    Item = q.get_menuitem(category,item)
    owner = (Item and Item.user_id == login_session.get('user_id',False))
    if not owner:
        flash("You are not authorized to edit this Item.\
                  Please create your own Item in order to edit.")
        return redirect("/catalog")
    Categories = q.get_catalog()
    status = False
    if Item and owner:
        if request.method == 'POST':
            newtitle = str(request.form['title']).strip()
            newdescription = str(request.form['description']).strip()
            newcategory = str(request.form['category']).strip()
            user_id = login_session['user_id']
            exists = q.get_menuitem(newcategory,newtitle)

            # delete item from old category and add to the new category
            if newcategory != category:
                # make sure item doe not exist on the new caegory
                if not exists:
                    status = \
                    q.addMenuItem(newtitle,newdescription,newcategory,user_id)
                else:
                    flash("Item already exists in %s " % newcategory)
                # delete item from old existing category if Successfully already
                # added to the new existing category
                if status:
                    q.deleteMenuItem(Item)
                    flash("Item successfully edited onto %s " % newcategory)
                    return redirect(url_for('catalogMenu'))
            elif Item.title == newtitle and Item.description == newdescription:
                flash("Item could not be edited. No changes detected!")
                return render_template('edititem.html', categories = Categories,
                                    target = category , title = newtitle,
                                    description = newdescription )
            else:
                status = q.editMenuItem(Item,newtitle,newdescription)
                if status:
                    flash("Item Successfully Edited.")
                    return redirect(url_for('catalogMenu'))

        return render_template('edititem.html', categories = Categories,
                                target = category , title = Item.title,
                                description = Item.description )
    else:
        return render_template('opps.html')


@app.route('/catalog/item/add',methods=['GET','POST'])
@login_required
def addMenuItem():
    Categories = q.get_catalog()
    if request.method == 'POST':
        newtitle = str(request.form['title']).strip()
        newdescription = str(request.form['description']).strip()
        category = str(request.form['category']).strip()
        user_id = login_session['user_id']
        # check if item exists
        exists = q.get_menuitem(category,newtitle)

        if not exists:
            status = q.addMenuItem(newtitle,newdescription,category,user_id)
            if status:
                flash("Item Successfully Added.")
                return redirect(url_for('catalogMenu'))

        flash("Item could not be added. Item already exists!")
        # Returns users last input
        return render_template('additem.html', categories = Categories,
                            target = category, title = newtitle,
                            description =  newdescription, navadd = "active")

    return render_template('additem.html', categories = Categories,
                            navadd = "active")


@app.route('/catalog/<category>/<item>/delete', methods=['GET','POST'])
@login_required
def deleteMenuItem(category,item):
    Item = q.get_menuitem(category,item)
    owner = ( Item and Item.user_id == login_session.get('user_id',False))
    if not owner:
        flash("You are not authorized to delete this Item.\
               Please create your own Item in order to delete.")
        return redirect("/catalog")
    status = False
    if Item and owner:
        if request.method == 'POST':
            q.deleteMenuItem(Item)
            flash("Menu Item Successfully Delete")
            return redirect(url_for('catalogMenu'))
        else:
            return render_template('deleteitem.html', category = category,
                                    item = item)
    else:
        return render_template('opps.html', category = category, item = item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    #app.run(host='0.0.0.0', port=8000)
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port = port)
