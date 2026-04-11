from sqlmodel import SQLModel, Session, create_engine
from .models import *

class Database:
    def __init__(self, db_path='BoardGameHub.db'):
        self.db_path = db_path

    def connect(self):
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=True)
        SQLModel.metadata.create_all(self.engine)

    def get_engine(self):
        return self.engine


db = Database()

def get_session():
    with Session(db.get_engine()) as session:
        yield session