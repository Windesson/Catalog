from flask import jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Category,MenuItem, User


engine = create_engine('sqlite:///catalogmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


def get_catalog():
    """ Selects all categories """
    return session.query(Category).all()


def get_catalogbyname(category_name):
    """ Selects a specific category by name  """
    return session.query(Category).filter_by(name = category_name).one()


def get_menuitem(category_name,item_title):
    try:
        category = get_catalogbyname(category_name)
        return session.query(MenuItem).filter_by(category_id = category.id,
                                                  title = item_title).all()[0]
    except:
        return False


def get_allmenuitem(category_name):
    """ Selects all items in a scpecific category by name  """
    try:
        category = get_catalogbyname(category_name)
        return get_menuitembycategoryid(category.id)
    except:
        return False


def get_latestitems():
    """ Selects latest 10 items """
    return session.query(MenuItem).order_by(desc(MenuItem.created_date)).limit(10).all()


def get_menuitembycategoryid(category_id):
    """ Selects all items in the category by id  """
    try:
        return session.query(MenuItem).filter_by(category_id = category_id).all()
    except:
        return False


def get_menuitembycategoryname(category_name):
    """ Selects all items in a scpecific category by name  """
    try:
        category = get_catalogbyname(category_name)
        return get_menuitembycategoryid(category.id)
    except:
        return False


def get_menuitembyuserid(user_id):
    """ Selects all items by specific user_id  """
    try:
        return session.query(MenuItem).filter_by(user_id = user_id).all()
    except:
        return False

def editMenuItem(Item,newtitle,newdescription):
    """ Update a specific item """
    try:
        Item.title = newtitle
        Item.description = newdescription
        session.commit()
        return True
    except:
        return False

def addMenuItem(newtitle,newdescription,category_name,user_id):
    """ Add a new item to a existing category """
    try:
        existing_category =  get_catalogbyname(category_name)
        Newmenuitem = MenuItem(user_id = user_id, title = newtitle,
                               description = newdescription,
                               category_id = existing_category.id)
        session.add(Newmenuitem)
        session.commit()
        return True
    except:
        return False


def deleteMenuItem(Item):
    """ Delete a existing item """
    session.delete(Item)
    session.commit()


def get_catalog_json():
    """ Select all optiong in the catalog and their items """
    catalogs_list = [c.serialize for c in get_catalog()]
    # Add items
    for c in catalogs_list:
        items = []
        for menu in get_menuitembycategoryid(c["id"]):
            items.append(menu.serialize)
        c["items"]= items

    return jsonify(Category=catalogs_list)


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
