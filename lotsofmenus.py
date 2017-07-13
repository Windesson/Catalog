from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, MenuItem, User

engine = create_engine('sqlite:///catalogmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Silva", email="walme004@fiu.edu",
             picture='https://lh3.googleusercontent.com/-PsNQO2WQH58/VzzAZq7QjHI/AAAAAAAAAro/9u_b3bp4PgIx9bqUSgbuOMDDctDCV0zcACEwYBhgL/w140-h140-p/silva.jpg')
session.add(User1)
session.commit()

newcategory = Category( user_id=1, name = "Soccer" )
session.add(newcategory)
session.commit()
# add item
newitem = MenuItem( user_id=1, title = "Two shinguards",
                        description = "occer shin guards from adidas",
                        category_id= 1)
session.add(newitem)
session.commit()

newitem = MenuItem( user_id=1, title = "Shinguards",
                    description = "soccer shin guards from adidas",
                    category_id= 1)
session.add(newitem)
session.commit()

newitem = MenuItem( user_id=1, title = "Jersey",
                    description = "Nikes Jersey",
                    category_id= 1)
session.add(newitem)
session.commit()

newitem = MenuItem( user_id=1, title = "Soccer Cleats",
                    description = "Nikes Soccer Cleats",
                    category_id= 1)
session.add(newitem)
session.commit()

newcategory = Category( user_id=1, name = "Hockey" )
session.add(newcategory)
session.commit()

newitem = MenuItem( user_id=1, title = "Stick",
                    description = "Nikes Stick",
                    category_id= 2)
session.add(newitem)
session.commit()

newcategory = Category( user_id=1, name = "Snowboarding" )
session.add(newcategory)
session.commit()

newitem = MenuItem( user_id=1, title = "Goggles",
                    description = "Nikes goggles",
                    category_id= 3)
session.add(newitem)
session.commit()

newitem = MenuItem( user_id=1, title = "Snowboard",
                    description = "Nikes Snowboard",
                    category_id= 3)
session.add(newitem)
session.commit()

newcategory = Category( user_id=1, name = "Frisbee" )
session.add(newcategory)
session.commit()

newitem = MenuItem( user_id=1, title = "Frisbee",
                    description = "Nikes Frisbee",
                    category_id= 4)
session.add(newitem)
session.commit()


newcategory = Category( user_id=1, name = "Baseball" )
session.add(newcategory)
session.commit()

newitem = MenuItem( user_id=1, title = "Bat",
                    description = "Nikes Bat",
                    category_id= 5)
session.add(newitem)
session.commit()


newcategory = Category( user_id=1, name = "Rock Climbing" )
session.add(newcategory)
session.commit()


newcategory = Category( user_id=1, name = "Foosball" )
session.add(newcategory)
session.commit()

newcategory = Category( user_id=1, name = "Skating" )
session.add(newcategory)
session.commit()


print "added menu items!"
