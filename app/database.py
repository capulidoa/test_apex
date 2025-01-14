from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///test.db" 

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    session = Session(engine)
    return session
