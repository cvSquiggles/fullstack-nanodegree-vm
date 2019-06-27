from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Genre, Base, Game, User

engine = create_engine('sqlite:///gameCatalog.db')
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

#Genre1 = Genre(name="Role-playing Game")
#session.add(Genre1)
#session.commit()



Game1 = Game(name="Gears of War", esrb="M",
 desc="Gory visceral over the top violence, mixed with tactical and surprisingly in depth combat systems.",
 releaseYear="2006", platforms="Xbox 360, PC", genreID=2, user_id=1)
print(Game1.desc)
session.add(Game1)
session.commit()
input("Press enter...")