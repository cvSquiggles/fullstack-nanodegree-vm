from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session = DBSession()

allRestaurants = session.query(Restaurant).all()

for i in allRestaurants:
    print("{}\n".format(i.name))

#peepumsNastyCream = session.query(MenuItem).filter_by(name = 'Spinach Ice Cream').one()

#print(peepumsNastyCream.name, peepumsNastyCream.id, peepumsNastyCream.restaurant.name)

#session.delete(peepumsNastyCream)
#session.commit()

####################################################################

#vegBurgers = session.query(MenuItem).filter_by(id = '10').one()

#vegBurgers.price = '2.99',

#session.add(vegBurgers)

#session.commit()

#print vegBurgers.price
#print vegBurgers.restaurant.name
#print vegBurgers.id

##for vegBurger in vegBurgers:
##    print vegBurger.id
##    print vegBurger.price
##    print vegBurger.restaurant.name
##    print ('\n')