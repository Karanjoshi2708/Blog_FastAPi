from sqlalchemy import String, Integer, Column ,Text
from database import Base

#Blog Table
class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)