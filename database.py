from sqlalchemy import (MetaData, Table, Column, Integer, DateTime, ForeignKey,
                        String, JSON, create_engine, PrimaryKeyConstraint)
from sqlalchemy.orm import sessionmaker, load_only
from sqlalchemy.ext.declarative import declarative_base


meta = MetaData()
Base = declarative_base(metadata=meta)


class Record(Base):
    """
    Enhancement simulation record model
    """
    __tablename__ = 'record'
    id = Column(Integer, primary_key=True)
    used_bases = Column(Integer, default=0)

    # Im too lazy to use JSON fields.
    pri_attempts = Column(Integer, default=0)
    pri_success = Column(Integer, default=0)
    pri_fail = Column(Integer, default=0)

    duo_attempts = Column(Integer, default=0)
    duo_success = Column(Integer, default=0)
    duo_fail = Column(Integer, default=0)

    tri_attempts = Column(Integer, default=0)
    tri_success = Column(Integer, default=0)
    tri_fail = Column(Integer, default=0)

    tet_attempts = Column(Integer, default=0)
    tet_success = Column(Integer, default=0)
    tet_fail = Column(Integer, default=0)

    pen_attempts = Column(Integer, default=0)
    pen_success = Column(Integer, default=0)
    pen_fail = Column(Integer, default=0)


class EnhanceDB:
    """
    Database handler for Enhance
    """
    engine = None
    session = None
    db_url=None

    def __init__(self, db_url=None):
        if db_url:
            self.db_url = db_url
        else:
            self.db_url = 'sqlite:///enhance.sqlite3'

    def start(self):
        self.engine = create_engine(self.db_url, echo=False)

        # Initialize Tables
        self.create_schema()
        # Initialize session
        self.create_session()
        return self.engine

    def create_schema(self):
        if not self.engine:
            raise Exception('Tables cannot be initialized. Engine has not been started.')
        return meta.create_all(self.engine)

    def create_session(self):
        if not self.engine:
            raise Exception('Session cannot be initialized. Engine has not been started.')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        return self.session

    def save_object(self, obj, commit=True):
        if not self.session:
            raise Exception('Save failed. Session not initialized.')
        try:
            self.session.add(obj)
            self.session.flush()
        except Exception:
            # Entry already exists in the DB
            self.session.rollback()
        if commit:
            return self.session.commit()
        return None

    def get_records(self):
        query = self.session.query(Record)
        query = query.all()
        return query
