# from sqlalchemy import Column, Integer, String
# from app.database.connection import Base
#
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50), unique=True, index=True, nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     password = Column(String(200), nullable=False)
#     role_id = Column(Integer, nullable=True)
