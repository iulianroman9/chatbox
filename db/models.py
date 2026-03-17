from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from db.database import Base


class UserRecord(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    files = relationship(
        "FileRecord", back_populates="owner", cascade="all, delete-orphan"
    )


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_name = Column(String, nullable=False)
    generated_name = Column(String, nullable=False, unique=True)
    content_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("UserRecord", back_populates="files")
    contents = relationship(
        "FileContentRecord",
        back_populates="file",
        cascade="all, delete-orphan",
    )


class FileContentRecord(Base):
    __tablename__ = "file_content"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    content_tsv = Column(TSVECTOR, nullable=False)
    embedding = Column(Vector(2048), nullable=False)

    __table_args__ = (
        Index("ix_file_content_content_tsv", "content_tsv", postgresql_using="gin"),
    )

    file = relationship("FileRecord", back_populates="contents")
