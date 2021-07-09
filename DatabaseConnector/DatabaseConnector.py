import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists
from sqlalchemy.orm import sessionmaker
import random
from dotenv import load_dotenv
import os
from langdetect import detect

Base = declarative_base()


class DatabaseConnector:
    def __init__(self):
        load_dotenv()
        self.USER = os.getenv('USER')
        self.PASSWORD = os.getenv('PASSWORD')
        self.HOST = os.getenv('HOST')
        self.PORT = os.getenv('PORT')
        self.DATABASE = os.getenv('DATABASE')

    def load_session(self):
        connection_string = "postgresql://" + self.USER + ":" + self.PASSWORD + "@" + self.HOST + "/" \
                             + self.DATABASE
        engine = sa.create_engine(connection_string, echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        return session

    def store(self, queue):
        session = self.load_session()
        try:
            while True:
                if not queue.empty():
                    character_info = queue.get()
                    char_exists = session.query(exists().where(Characters.name == character_info.name)).scalar()
                    if not char_exists:
                        session.add(character_info)
                        session.commit()

                    '''# check if there's a character in DB with a different price from scraping result. If so, update it.
                    else:
                        query_exists = session.query(Characters).filter(Characters.name == character_info.name,
                                                              Characters.current_price == character_info.current_price)

                        if not query_exists:
                            query_exists.update({Characters.current_price: character_info.current_price})
                            session.commit()'''
        finally:
            session.close()

    def get_polack_nickname(self):
        polacks = self.get_polacks_nicknames()
        random_polack = random.choice(polacks)
        return random_polack

    def get_polacks_nicknames(self):
        session = self.load_session()
        polack_nicknames = session.query(Characters.name).filter(Characters.nationality == 'pl')
        session.close()
        return polack_nicknames

    def get_polacks(self):
        session = self.load_session()
        polack_chars = session.query(Characters.name, Characters.level, Characters.vocation, Characters.auction_id).\
            filter(Characters.nationality == 'pl').order_by(Characters.level.desc())
        session.close()
        return polack_chars


class Characters(Base):
    __tablename__ = "tibiachars"
    id = sa.Column('id', sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String(50))
    level = sa.Column('level', sa.Integer)
    vocation = sa.Column('vocation', sa.String(30))
    gender = sa.Column('gender', sa.String(20))
    world = sa.Column('world', sa.String(30))
    auction_end = sa.Column('auction_end', sa.String(50))
    current_price = sa.Column('current_price', sa.Integer)
    auction_id = sa.Column('auction_id', sa.Integer)
    nationality = sa.Column('nationality', sa.String(50))

    def __init__(self, name, level, vocation, gender, world, auction_end, current_price, auction_id):
        self.name = name
        self.level = level
        self.vocation = vocation
        self.gender = gender
        self.world = world
        self.auction_end = auction_end
        self.current_price = current_price
        self.auction_id = auction_id
        self.nationality = detect(name)

    def __repr__(self):
        return "<Characters({}, {}, {}, {}, {}, {}, {}, {})>".format(self.name, self.level, self.vocation,
                                                                     self.gender, self.world, self.auction_end,
                                                                     self.current_price, self.auction_id)
