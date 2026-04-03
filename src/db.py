from sqlmodel import SQLModel, create_engine
from models import User

class Database:
    def __init__(self, db_path='BoardGameHub.db'):
        self.db_path = db_path

    def connect(self):
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=True)
        SQLModel.metadata.create_all(self.engine)