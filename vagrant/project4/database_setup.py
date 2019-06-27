#!usr/bin/env python3

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Genre(Base):
    __tablename__ = 'genre'

    name = Column(
        String(80), nullable = False)

    id = Column(
        Integer, primary_key = True)

class Game(Base):
    __tablename__ = 'game'

    name = Column(
        String(80), nullable = False)

    id = Column(
        Integer, primary_key = True)

    esrb = Column(
        String(80))

    desc = Column(
        String(300))

    releaseYear = Column(
        String(80))

    platforms = Column(
        String(80))

    genreID = Column(
        Integer, ForeignKey('genre.id'))

    genre = relationship(Genre)

    user_id = Column(Integer,ForeignKey('user.id'))

    user = relationship(User)

    @property
    def serialize(self):
        #Later JSON interaction
        return {
            'name'          :self.name,
            'esrb'          :self.esrb,
            'desc'          :self.desc,
            'releaseYear'   :self.releaseYear,
            'platforms'     :self.platforms,
        }

##############Build engine#######################

engine = create_engine(
    'sqlite:///gameCatalog.db')

Base.metadata.create_all(engine)    